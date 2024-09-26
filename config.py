import os

class Config:
    # Configuration for PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/TicketGrabdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
