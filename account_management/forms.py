# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, EmailField, DateField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    submit = SubmitField('Submit')

