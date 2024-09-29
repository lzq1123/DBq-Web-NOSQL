import os

class Config:
    # Configuration for PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:19V28ydb@localhost/TicketGrabdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
