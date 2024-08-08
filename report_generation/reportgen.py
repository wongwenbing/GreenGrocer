from wtforms import Form, DateField, RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
import sys
#set system paath
sys.path.append('../GreenGrocer')
from db import db_connector
db, cursor = db_connector()

class customer_report:
    def __init__(self, custid, startdate, end_date, reporttype):
        self.custid = custid
        self.startdate = startdate
        self.end_date = end_date
        self.report_type = reporttype

    def to_db(self):
        query="""
        INSERT INTO Customer_Report(customer_id, coverage_start, coverage_end, report_type)
        VALUES (%s, %s, %s, %s)
        """
        string = (self.custid, self.startdate, self.end_date, self.report_type)
        cursor.execute(query, string)
        db.commit()
        print("Succcessfully committed")


    def info(self):
        return (f"Start: {self.startdate}, End: {self.end_date}"
                f"Fields: {self.report_type}")

class Report(Form):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])

class CustReport(Report):
    type_of_report =  RadioField('Report Type', choices=[
        ('Purchasing', 'Purchasing History'),
        ('Sustainability', 'Sustainability Report')
    ])

class StaffReport(Report):
    type_of_report = RadioField('Report Type', choices=[
        ('Sales', 'Sales'),
        ('Category', 'Product Categories'),
        ('Inventory', 'Inventory')
    ])

class staff_report:
    def __init__(self, staff_id, startdate, end_date, reporttype):
        self.staffid = staff_id
        self.startdate = startdate
        self.end_date = end_date
        self.report_type = reporttype

    def to_db(self):
        query = """
        INSERT INTO Staff_Report(staff_id, coverage_start, coverage_end, report_type)
        VALUES (%s, %s, %s, %s)
        """
        string = (self.staffid, self.startdate, self.end_date, self.report_type)
        cursor.execute(query, string)
        db.commit()
        print("Succcessfully committed")

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

class Retrieve_Staff_Report:
    def __init__(self, reportid, staffid, startdate, enddate, report_type):
        self.reportid = reportid
        self.staffid = staffid
        self.start_date = startdate
        self.end_date = enddate
        self.report_type = report_type


#
# r = staff_report(1, '2023-01-01', '2023-03-31', 'Category')
# r.to_db()