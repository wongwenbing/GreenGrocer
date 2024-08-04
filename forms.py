from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, DecimalField
from flask_wtf import FlaskForm

class FilterForm(Form):
    min_price = DecimalField('Min Price')
    max_price = DecimalField('Max Price')