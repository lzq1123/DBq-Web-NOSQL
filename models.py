from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(320), unique=True, nullable=False)
    Password = db.Column(db.String(128), nullable=False)  # Assuming hashed storage
    PaymentMethod = db.relationship('PaymentMethod', back_populates='User', uselist=False)
    Transactions = db.relationship('Transaction', back_populates='User')

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
    User = db.relationship('Users', back_populates='PaymentMethod')

class Location(db.Model):
    __tablename__ = 'Location'
    LocationID = db.Column(db.Integer, primary_key=True)
    VenueName = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(100), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)
    Events = db.relationship('Event', back_populates='Location')

class Event(db.Model):
    __tablename__ = 'Event'
    EventID = db.Column(db.Integer, primary_key=True)
    EventName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(300))
    EventDate = db.Column(db.DateTime, nullable=False)
    LocationID = db.Column(db.Integer, db.ForeignKey('Location.LocationID'))
    Tickets = db.relationship('Ticket', back_populates='Event')
    Queues = db.relationship('Queue', back_populates='Event')
    Location = db.relationship('Location', back_populates='Events')

class Ticket(db.Model):
    __tablename__ = 'Ticket'
    TicketID = db.Column(db.Integer, primary_key=True)
    EventID = db.Column(db.Integer, db.ForeignKey('Event.EventID'))
    SeatNo = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    Transaction = db.relationship('Transaction', back_populates='Ticket', uselist=False)
    Category = db.relationship('TicketCategory', back_populates='Tickets')

class TicketCategory(db.Model):
    __tablename__ = 'TicketCategory'
    CatID = db.Column(db.Integer, primary_key=True)
    Price = db.Column(db.Numeric, nullable=False)
    Tickets = db.relationship('Ticket', back_populates='Category')

class Transaction(db.Model):
    __tablename__ = 'Transaction'
    TranscID = db.Column(db.Integer, primary_key=True)
    TranAmount = db.Column(db.Numeric, nullable=False)
    TransDate = db.Column(db.DateTime, default=datetime.utcnow)
    TranStatus = db.Column(db.String(50), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    CardID = db.Column(db.Integer, db.ForeignKey('PaymentMethod.CardID'))
    TicketID = db.Column(db.Integer, db.ForeignKey('Ticket.TicketID'))
    User = db.relationship('Users', back_populates='Transactions')
    Ticket = db.relationship('Ticket', back_populates='Transaction')

class Queue(db.Model):
    __tablename__ = 'Queue'
    QueueID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    EventID = db.Column(db.Integer, db.ForeignKey('Event.EventID'))
    User = db.relationship('Users', backref='QueueEntries')
    Event = db.relationship('Event', backref='QueueEntries')
