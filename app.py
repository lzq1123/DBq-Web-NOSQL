from flask import Flask, render_template, request, session, url_for, redirect
from config import Config
from sqlalchemy import text, extract
from sqlalchemy.orm import joinedload
from api.ticketmaster import fetch_and_store_events
import logging, traceback
from datetime import datetime
import calendar
import bcrypt
from auth import hash_password, verify_password, RegistrationForm, LoginForm

from models import db, Users, PaymentMethod, Location, Event, Ticket, TicketCategory, Transaction, Queue
from auth import hash_password, verify_password

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = Config.APP_SECRET_KEY
app.config.from_object(Config)
db.init_app(app)

API_KEY = Config.TICKETMASTER_API_KEY

# Check connection and create tables if not already created
with app.app_context():
    try:
        # Test the connection to the database
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            print(f"Connection to database successful! Result: {result}")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        if not tables:
            db.create_all()
            logging.info("Tables created successfully!")
            fetch_and_store_events(API_KEY, 50)
        else:
            print("All tables are already created, no action needed.")
    except Exception as e:
        logging.error(f"Error:{e}\n{traceback.format_exc()}")

# Routes
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/event')
def event():
    events_by_month_year = {}
    preferred_width = 1920

    # Fetch all events and sort them by year and day within each year
    events = Event.query.options(joinedload(Event.image)).order_by(Event.EventDate).all()

    for event in events:
        # If there are images associated with the event, choose one closest to the preferred width
        if event.image:
            event.preferred_image = min(event.image, key=lambda img: abs(img.Width - preferred_width))
        else:
            event.preferred_image = None  # Set to None if no images exist

        month_year = f"{calendar.month_name[event.EventDate.month]} {event.EventDate.year}"
        if month_year not in events_by_month_year:
            events_by_month_year[month_year] = []
        events_by_month_year[month_year].append(event)

    current_year = datetime.now().year
    sorted_month_years = sorted(
        events_by_month_year.keys(),
        key=lambda x: (int(x.split(' ')[1]), -1 if int(x.split(' ')[1]) == current_year else 0)
    )

    return render_template('event.html', events_by_month_year={key: events_by_month_year[key] for key in sorted_month_years})

@app.route('/venue')
def venue():
    preferred_width = 1920
    venues_with_images = []

    locations = Location.query.options(joinedload(Location.image)).all()

    for location in locations:

        # If there are images associated with the event, choose one closest to the preferred width
        if location.image:
            location.preferred_image = min(location.image, key=lambda img: abs(img.Width - preferred_width))
        else:
            location.preferred_image = None  # Set to None if no images exist

        venues_with_images.append({
            'VenueName': location.VenueName,
            'Address': location.Address,
            'Country': location.Country,
            'State': location.State,
            'PostalCode': location.PostalCode,
            'ImageURL': location.preferred_image.URL if location.preferred_image else 'path/to/default/image.jpg'
        })

    return render_template('venue.html', venues=venues_with_images)

@app.route('/registersignup')
def registersignup():
    registration_form = RegistrationForm()
    login_form = LoginForm()
    return render_template('registersignup.html', registration_form=registration_form, login_form=login_form)

@app.route('/register', methods=['POST'])
def register():
    registration_form = RegistrationForm(request.form)
    login_form = LoginForm()
    if registration_form.validate_on_submit():
        email = registration_form.email.data
        existing_user = Users.query.filter_by(Email=email).first()
        if existing_user:
            error_message = 'Email already registered.'
            return render_template('registersignup.html', registration_form=registration_form, login_form=login_form, error_message=error_message)

        hashed_password = bcrypt.hashpw(registration_form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = Users(
            Name=registration_form.name.data,
            Email=email,
            Password=hashed_password,
            Phone=registration_form.phone.data
        )
        
        db.session.add(new_user)
        db.session.commit()
        error_message = 'You have successfully registered!'
        return render_template('login', error_message=error_message)
    else:
        logging.error("Form Errors:", registration_form.errors)
        for field, errors in registration_form.errors.items():
            for error in errors:
                error_message += f"Error in the {getattr(registration_form, field).label.text} field - {error} "
    return render_template('registersignup.html', registration_form=registration_form, login_form=login_form, error_message=error_message)

@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm(request.form)
    registration_form = RegistrationForm()

    email = login_form.email.data
    password = login_form.password.data
    
    if login_form.validate_on_submit():
        user = Users.query.filter_by(Email=email).first()

        if user and bcrypt.checkpw(login_form.password.data.encode('utf-8'), user.Password.encode('utf-8')):
            session['user_id'] = user.UserID
            error_message = 'Login successful!'
            return render_template('landing.html', error_message=error_message)
        else:
            error_message = 'Invalid email or password'
            return render_template('registersignup.html', login_form=login_form, registration_form=registration_form, error_message=error_message)
    else:
        logging.error("Form Errors:", login_form.errors) 
        for fieldName, errorMessages in login_form.errors.items():
            for err in errorMessages:
                error_message += f'{fieldName}: {err} '

    return render_template('registersignup.html', login_form=login_form, registration_form=registration_form, error_message=error_message) 

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    error_message = 'You have been logged out.'
    return render_template('landing.html', error_message=error_message)

@app.route('/myticket')
def myticket():
        return render_template('myticket.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/ticket/<event_id>')
def ticket(event_id):
    event_with_images = []
    error_message = None
    preferred_width = 1920

    user_id = session.get('user_id')
    user = Users.query.get(user_id)
    event = Event.query.options(joinedload(Event.image)).filter_by(EventID=event_id).first()
    if not event:
        error_message = "Event not found!"
        return redirect(url_for('landing'))

    if event.image:
        event.preferred_image = min(event.image, key=lambda img: abs(img.Width - preferred_width))
    else:
        event.preferred_image = None

    event_with_images = {
        'EventName': event.EventName,
        'EventDate': event.EventDate.strftime('%d %b %Y'),
        'ImageURL': event.preferred_image.URL if event.preferred_image else url_for('static', filename='images/default.jpg')
    }

    return render_template('ticket.html', error_message=error_message, event=event_with_images, user=user)

@app.route('/event/<event_id>/purchase', methods=['GET', 'POST'])
def purchase_tickets(event_id):
    # Querying ticket categories available for this event
    event = Event.query.filter_by(EventID=event_id).first()
    ticket_categories = event.ticketCategory if event else []

    if request.method == 'POST':
        user_id = session.get('user_id')
        category_id = request.form.get('category')
        quantity = int(request.form.get('quantity'))
        cardholder_name = request.form.get('cardholder-name')
        card_number = request.form.get('card-number')
        cvv = request.form.get('cvv')
        expiry_month = request.form.get('expiry-month')
        expiry_year = request.form.get('expiry-year')
        billing_address = request.form.get('billing-address')

        # Creating a new PaymentMethod entry
        payment_method = PaymentMethod(
            UserID=user_id,
            CardNumber=card_number,
            CVV=cvv,
            CardType='Unknown',  # Update this accordingly if you have card type info
            ExpireDate=datetime(int(expiry_year), int(expiry_month), 1),
            BillAddr=billing_address,
            CardHolderName=cardholder_name
        )
        db.session.add(payment_method)
        db.session.commit()

        # Creating a new Transaction entry
        ticket_category = TicketCategory.query.get(category_id)
        total_price = ticket_category.CatPrice * quantity
        transaction = Transaction(
            TranAmount=total_price,
            TranStatus='Completed',
            UserID=user_id,
            TicketID=None  # Assuming this needs to be updated after ticket creation
        )
        db.session.add(transaction)
        db.session.commit()

        error_message = 'Purchase successful!'
        return render_template('landing.html')

    return render_template('ticket.html', ticket_categories=ticket_categories)

@app.route('/venueinfo')
def venueinfo():
    return render_template('venueinfo.html')

if __name__ == "__main__":
    app.run(debug=True)
