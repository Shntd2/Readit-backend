from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    client_hashed_password = PasswordField('Hashed Password', validators=[
        DataRequired(),
        Length(min=64, max=64, message="Client-hashed password must be exactly 64 characters long")
    ])
    confirm_client_hashed_password = PasswordField('Confirm Hashed Password', validators=[
        DataRequired(),
        EqualTo('client_hashed_password', message='Hashed passwords must match'),
        Length(min=64, max=64, message="Client-hashed password must be exactly 64 characters long")
    ])
    submit = SubmitField('Sign Up')
