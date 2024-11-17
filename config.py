import os
class Config:
    # Configuration for PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = 'postgresql://ticketgrab:strawberries@ticketgrab.cly1peobyaye.us-east-1.rds.amazonaws.com:5432/ticketgrabdb'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/ticketgrabdb'
    QLALCHEMY_TRACK_MODIFICATIONS = False
    TICKETMASTER_API_KEY = 'eX1Cju21ITBzuzX7qEi0vUlQacKAARt6'
    APP_SECRET_KEY = 'strawberries'