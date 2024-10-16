from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    client_hashed_password = PasswordField('Client Hashed Password', validators=[DataRequired(), Length(min=64, max=64)])


class ChangePasswordForm(FlaskForm):
    current_client_hashed_password = PasswordField('Current Client Hashed Password', validators=[DataRequired(), Length(min=64, max=64)])
    new_client_hashed_password = PasswordField('New Client Hashed Password', validators=[DataRequired(), Length(min=64, max=64)])
    confirm_client_hashed_password = PasswordField('Confirm New Client Hashed Password', validators=[
        DataRequired(),
        EqualTo('new_client_hashed_password', message='Passwords must match'),
        Length(min=64, max=64)
    ])
