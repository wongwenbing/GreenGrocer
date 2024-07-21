from wtforms import Form, RadioField, SelectMultipleField, TextAreaField, validators

class CreateCustReport(Form): 
    description = TextAreaField('Description', [validators.length(1)])
    categories = SelectMultipleField(
        choices = [('1', 'Customer Sign Up Date'), ('2', 'Customer Date')]
    )