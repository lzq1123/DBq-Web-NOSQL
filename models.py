from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(320), unique=True, nullable=False)
    Password = db.Column(db.String(128), nullable=False)  
    Phone = db.Column(db.String(20), nullable=False)
    paymentMethod = db.relationship('PaymentMethod', back_populates='users', uselist=False)
    transaction = db.relationship('Transaction', back_populates='users')

class PaymentMethod(db.Model):
    __tablename__ = 'PaymentMethod'
    CardID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), unique=True)
    CardNumber = db.Column(db.String(16), nullable=False)
    CVV = db.Column(db.String(4), nullable=False)
    CardType = db.Column(db.String(50), nullable=False)
    ExpireDate = db.Column(db.DateTime, nullable=False)
    BillAddr = db.Column(db.String(500), nullable=False)
    CardHolderName = db.Column(db.String(100), nullable=False)
    users = db.relationship('Users', back_populates='paymentMethod')

class Location(db.Model):
    __tablename__ = 'Location'
    LocationID = db.Column(db.String(20), primary_key=True)
    VenueName = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(100), nullable=False)
    Country = db.Column(db.String(50), nullable=False)
    State = db.Column(db.String(50), nullable=False)
    PostalCode = db.Column(db.String(10), nullable=False)
    event = db.relationship('Event', back_populates='location')
    image = db.relationship('Image', back_populates='location')

class Event(db.Model):
    __tablename__ = 'Event'
    EventID = db.Column(db.String(20), primary_key=True)
    EventName = db.Column(db.String(100), nullable=False)
    EventDate = db.Column(db.DateTime, nullable=False)
    EventType = db.Column(db.String(100))
    LocationID = db.Column(db.String(20), db.ForeignKey('Location.LocationID'))
    ticketCategory = db.relationship('TicketCategory', back_populates='event')
    queue = db.relationship('Queue', back_populates='event')
    location = db.relationship('Location', back_populates='event')
    image = db.relationship('Image', back_populates='event')
class Ticket(db.Model):
    __tablename__ = 'Ticket'
    TicketID = db.Column(db.Integer, primary_key=True)
    CatID = db.Column(db.Integer, db.ForeignKey('TicketCategory.CatID'))
    EventID = db.Column(db.String(20), db.ForeignKey('Event.EventID'))
    SeatNo = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    TranscID = db.Column(db.Integer, db.ForeignKey('Transaction.TranscID'))
    transaction = db.relationship('Transaction', back_populates='ticket')
    ticketCategory = db.relationship('TicketCategory', back_populates='ticket')
class TicketCategory(db.Model):
    __tablename__ = 'TicketCategory'
    CatID = db.Column(db.Integer, primary_key=True)
    EventID = db.Column(db.String(20), db.ForeignKey('Event.EventID'))
    CatName = db.Column(db.String(20), nullable=False)
    CatPrice = db.Column(db.Numeric, nullable=False)
    SeatsAvailable = db.Column(db.Numeric, nullable=False)
    ticket = db.relationship('Ticket', back_populates='ticketCategory')
    event = db.relationship('Event', back_populates='ticketCategory') 
class Transaction(db.Model):
    __tablename__ = 'Transaction'
    TranscID = db.Column(db.Integer, primary_key=True)
    TranAmount = db.Column(db.Numeric, nullable=False)
    TransDate = db.Column(db.DateTime, default=datetime.utcnow)
    TranStatus = db.Column(db.String(50), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    CardID = db.Column(db.Integer, db.ForeignKey('PaymentMethod.CardID'))
    users = db.relationship('Users', back_populates='transaction')
    ticket = db.relationship('Ticket', back_populates='transaction')

class Queue(db.Model):
    __tablename__ = 'Queue'
    QueueID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    EventID = db.Column(db.String(100), db.ForeignKey('Event.EventID'))
    users = db.relationship('Users', backref='QueueEntries')
    event = db.relationship('Event', back_populates='queue')

class Image(db.Model):
    __tablename__ = 'Image'
    ImageID = db.Column(db.Integer, primary_key=True)
    URL = db.Column(db.String(500), nullable=False)
    Ratio = db.Column(db.String(20), nullable=False)
    Width = db.Column(db.Integer, nullable=False)
    Height = db.Column(db.Integer, nullable=False)
    EventID = db.Column(db.String(20), db.ForeignKey('Event.EventID'))
    LocationID = db.Column(db.String(20), db.ForeignKey('Location.LocationID'))
    event = db.relationship('Event', back_populates='image')
    location = db.relationship('Location', back_populates='image')