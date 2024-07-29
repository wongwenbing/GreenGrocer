from wtforms import Form, RadioField, DateField

class CustomerReport(Form): 
    category = RadioField('Category', choices=['Sustainability', 'Spending', 'Nutrition'])
    coverage = DateField('Coverage Date')
    