from flask import Flask, render_template
from models import db, Users, PaymentMethod, Location, Event, Ticket, TicketCategory, Transaction, Queue
from config import Config
from sqlalchemy import text 

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

db.init_app(app)

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
            print("Tables created successfully!")
        else:
            print("All tables are already created, no action needed.")
    except Exception as e:
        print(f"Error: {e}")

# Routes
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/event')
def event():
    return render_template('event.html')

@app.route('/venue')
def venue():
    return render_template('venue.html')

@app.route('/registersignup')
def registersignup():
    return render_template('registersignup.html')

@app.route('/myticket')
def myticket():
        return render_template('myticket.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/ticket')
def ticket():
    return render_template('ticket.html')


@app.route('/venueinfo')
def venueinfo():
    return render_template('venueinfo.html')


if __name__ == "__main__":
    app.run(debug=True)
