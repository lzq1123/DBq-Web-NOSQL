import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=2)])
    email = StringField('Email', [validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=4, message="Password must be at least 4 characters long")
    ])
    phone = StringField('Phone', validators=[
        validators.DataRequired(),
        validators.Regexp(r'^\d{8,}$', message="Enter a valid phone number with at least 8 digits")
    ])

class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])