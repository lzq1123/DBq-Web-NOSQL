import os

class Config:
    # Configuration for PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://DBProjGrp38:strawberries@ticketgrabdb.cugroa0wbny6.us-east-1.rds.amazonaws.com:5432/TicketGrabdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
