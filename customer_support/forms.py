from wtforms import Form, StringField, DateField, TimeField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class TicketForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M:%S', validators=[DataRequired()])
    issue = TextAreaField("What's the issue?", validators=[DataRequired()])
    topic = SelectField('Topic', choices=[
        ('', 'Select a topic >'),
        ('Account Login Issue', 'Account Login Issue'),
        ('Account Management', 'Account Management'),
        ('Account Security', 'Account Security'),
        ('Billing Inquiry', 'Billing Inquiry'),
        ('Delivery Issue', 'Delivery Issue'),
        ('Delivery Status', 'Delivery Status'),
        ('Order Inquiry', 'Order Inquiry'),
        ('Order Issue', 'Order Issue'),
        ('Product Availability', 'Product Availability'),
        ('Product Enquiry', 'Product Enquiry'),
        ('Refund Request', 'Refund Request'),
        ('Refund Status', 'Refund Status'),
        ('Technical Status', 'Technical Status'),
        ('Subscription Renewal', 'Subscription Renewal'),
        ('Customer Support', 'Customer Support')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Submit')
