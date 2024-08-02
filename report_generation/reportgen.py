from wtforms import Form, DateField, RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class customer_report:
    def __init__(self, startdate, end_date, description, reporttype):
        self.startdate = startdate
        self.end_date = end_date
        self.description = description
        self.report_type = reporttype

    def to_db(self):
        query="""
        INSERT INTO Customer_Report (Customer_Id, 
        """

    def info(self):
        return (f"Start: {self.startdate}, End: {self.end_date}"
                f"Fields: {self.report_type}")

class Report(Form):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

class CustReport(Report):
    type_of_report =  RadioField('Report Type', choices=[
        ('Purchases', 'Purchasing History'),
        ('Sustainability', 'Sustainability Report')
    ])

class StaffReport(Report):
    type_of_report = RadioField('Report Type', choices=[
        ('Sales', 'Sales'),
        ('Products', 'Product'),
        ('Inventory', 'Inventory')
    ])

class staff_report():
    def __init__(self, startdate, end_date, description, reporttype):
        self.startdate = startdate
        self.end_date = end_date
        self.description = description
        self.report_type = reporttype

    def to_db(self):
        query = """
           INSERT INTO Customer_Report (Customer_Id, 
           """

    def info(self):
        return (f"Start: {self.startdate}, End: {self.end_date}"
                f"Fields: {self.report_type}")