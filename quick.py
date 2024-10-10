@app.route('/event')
def event():
    search_query = request.args.get('search', '').lower() 
    search_month = request.args.get('search_month')  
    page = request.args.get('page', 1, type=int)  
    events_per_page = 9  
    events_by_month_year = {}
    preferred_width = 1920
    search_date_parsed = None

    if search_month:
        try:
            search_date_parsed = datetime.strptime(search_month, '%Y-%m')
        except ValueError:
            search_date_parsed = None  

    base_query = Event.query.options(joinedload(Event.image)).order_by(Event.EventDate)

    if search_query and search_date_parsed:
        base_query = base_query.filter(
            and_(
                Event.EventName.ilike(f'%{search_query}%'),
                Event.EventDate.between(search_date_parsed.replace(day=1),
                                        search_date_parsed.replace(day=calendar.monthrange(search_date_parsed.year, search_date_parsed.month)[1]))
            )
        )
    elif search_query:
        base_query = base_query.filter(Event.EventName.ilike(f'%{search_query}%'))
    elif search_date_parsed:
        base_query = base_query.filter(
            Event.EventDate.between(search_date_parsed.replace(day=1),
                                    search_date_parsed.replace(day=calendar.monthrange(search_date_parsed.year, search_date_parsed.month)[1]))
        )

    # Pagination
    paginated_events = base_query.paginate(page=page, per_page=events_per_page)

    for event in paginated_events.items:
        if event.image:
            event.preferred_image = min(event.image, key=lambda img: abs(img.Width - preferred_width))
        else:
            event.preferred_image = None

        # Group events by month and year
        month_year = f"{calendar.month_name[event.EventDate.month]} {event.EventDate.year}"
        if month_year not in events_by_month_year:
            events_by_month_year[month_year] = []
        events_by_month_year[month_year].append(event)

    sorted_month_years = sorted(
        events_by_month_year.keys(),
        key=lambda x: (int(x.split(' ')[1]), -1 if int(x.split(' ')[1]) == datetime.now().year else 0)
    )

    return render_template(
        'event.html',
        events_by_month_year={key: events_by_month_year[key] for key in sorted_month_years},
        search_query=search_query,
        search_month=search_month, 
        current_page=page,
        total_pages=paginated_events.pages
    )

@app.route('/ticket/<event_id>')
def ticket(event_id):
    error_message = None
    preferred_width = 1920

    # Get user info from session
    user_id = session.get('user_id')
    user = Users.query.get(user_id)
    event = Event.query.options(joinedload(Event.image), joinedload(Event.ticketCategory)).filter_by(EventID=event_id).first()

    if not event:
        # flash("Event not found!", "error")
        return redirect(url_for('landing'))
    
    # Determine ticket availability
    tickets_available = any(
        category.SeatsAvailable > Ticket.query.filter_by(CatID=category.CatID).count()
        for category in event.ticketCategory
    )

    # Choose preferred image based on width
    if event.image:
        event.preferred_image = min(event.image, key=lambda img: abs(img.Width - preferred_width))
    else:
        event.preferred_image = None

    # Prepare event and user information for the template
    event_image = {
        'ImageURL': event.preferred_image.URL if event.preferred_image else url_for('static', filename='images/default.jpg')
    }
    return render_template('ticket.html', 
                           event=event, 
                           event_image=event_image,
                           user=user,
                           tickets_available=tickets_available)