import requests
from datetime import datetime
from models import db, Event, Image, Location, TicketCategory
import logging, traceback
from config import Config
from sqlalchemy import func
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = Config.TICKETMASTER_API_KEY

def fetch_and_store_events(api_key, total_events):
    base_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    # country_code = 'SG'
    events_fetched = 0
    page_number = 0

    while events_fetched < total_events:
        params = {
            'apikey': api_key,
            'size': 20,  # Max size as per API limit
            'page': page_number
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if 'events' in data['_embedded']:
            for event in data['_embedded']['events']:
                store_event(event)
                events_fetched += 1
                logging.info(f"{events_fetched} events fetched")
                if events_fetched >= total_events:
                    break
        page_number += 1

def store_event(event_data):            
    event = Event(
        EventID=event_data['id'],
        EventName=event_data['name'],
        EventDate=datetime.fromisoformat(event_data['dates']['start']['dateTime']),
        # Description=event_data.get('info', 'No description provided'),
        LocationID=event_data['_embedded']['venues'][0]['id'],
    )
    locationID = Location.query.filter_by(LocationID=event.LocationID).first()
    if not locationID:
        fetch_venue_by_id(API_KEY, event.LocationID)
    db.session.add(event)
    db.session.flush()  # Flush to get the event ID for image relationship
    logging.info(f"Event name: {event.EventName}, start date: {event.EventDate}, venue name: {event.LocationID}, id: {event.EventID} stored successfully!")

    min_price = event_data['priceRanges'][0]['min']
    max_price = event_data['priceRanges'][0]['max']

    store_ticket_category(min_price, max_price, event.EventID)
    if 'images' in event_data:
        store_image(event_data['images'], None, event.EventID)

def fetch_venue_by_id(api_key, venue_id):
    # Define the base URL for the Ticketmaster API
    base_url = "https://app.ticketmaster.com/discovery/v2/venues"
    
    # Construct the URL with the venue ID and include the API key as a query parameter
    url = f"{base_url}/{venue_id}.json?apikey={api_key}"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        location_data = response.json()
        store_location(location_data)
        
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}\n{traceback.format_exc()}")
    except Exception as e:
        logging.error(f"Error processing venue data: {e}\n{traceback.format_exc()}")

def store_location(location_data):
    new_location = Location(
        LocationID=location_data.get('id'),
        VenueName=location_data.get('name'),
        Address=location_data.get('address', {}).get('line1', 'No Address Provided'),
        Country=location_data.get('country', {}).get('name', 'No Country Provided'),
        State=location_data.get('state', {}).get('name', 'No State Provided'),
        PostalCode=location_data.get('postalCode', 'No Postal Code Provided'),
        Description=location_data.get('description')
        # Capacity = None
    )
    try:
        db.session.add(new_location)
        db.session.commit()
        logging.info(f"LocationID: {new_location.LocationID}, VenueName: {new_location.VenueName}")
        if 'images' in location_data:
            store_image(location_data['images'], new_location.LocationID, None)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to store location. Error: {e}\n{traceback.format_exc()}")
   

def store_ticket_category(min_price, max_price, event_id):
    category_names = ["Cat 1", "Cat 2", "Cat 3"]  # Example category names
    price_steps = (max_price - min_price) / 2
    try:
        for i in range(3):
            cat_price = min_price + i * price_steps
            # Create a new TicketCategory object
            ticket_category = TicketCategory(
                CatName=category_names[i],
                CatPrice=cat_price,
                SeatsAvailable=100,
                EventID=event_id
            )
            db.session.add(ticket_category)

        db.session.commit()  # Commit all added categories to the database
        logging.info("Ticket categories stored successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Failed to store ticket categories: {e}\n{traceback.format_exc()}")


def store_image(image_data, location_id, event_id):
    for image in image_data:
        image_id = db.session.query(func.max(Image.ImageID)).scalar()
        if image_id is not None:
            image_id += 1
        else:
            image_id = 1
        img = Image(
            ImageID = image_id,
            URL=image['url'],
            Ratio=image['ratio'],
            Width=image['width'],
            Height=image['height'],
            LocationID=location_id,
            EventID=event_id
        )
        db.session.add(img)
        image_id += 1
    db.session.commit()
    logging.info(f"Image id: {image_id}, LocationID: {img.LocationID}, Event id: {img.EventID}, url: {img.URL}, ratio: {img.Ratio}, Width: {img.Width},  Height: {img.Height} stored successfully!")
