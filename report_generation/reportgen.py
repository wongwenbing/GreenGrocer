from wtforms import Form, DateField, RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class customer_report:
    def __init__(self, startdate, end_date, reporttype):
        self.startdate = startdate
        self.end_date = end_date
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

class staff_report:
    def __init__(self, startdate, end_date, description, reporttype):
        self.startdate = startdate
        self.end_date = end_date
        self.report_type = reporttype

    def to_db(self):
        query = """
           INSERT INTO Customer_Report (Customer_Id, 
           """

    def info(self):
        return (f"Start: {self.startdate}, End: {self.end_date}"
                f"Fields: {self.report_type}")

class Retrieve_Customer_Report:
    def __init__(self, reportid, custid, startdate, enddate, report_type):
        self.reportid = reportid
        self.custid = custid
        self.start_date = startdate
        self.end_date = enddate
        self.report_type = report_type

# query="""
# SELECT *
# FROM customer_report
# WHERE customer_id = %s
# """
# cust_id = 1
# cursor.execute(query, cust_id)