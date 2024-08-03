import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector
db, cursor = db_connector()
import json

class PurchasingReport:
    def __init__(self, startdate, enddate, custid):
        self.startdate = startdate
        self.enddate = enddate
        self.custid = custid
        self.total = ""

    def get_total_amount(self):
        query = """
        SELECT * FROM Order
        """
        total = sum
        total =

    def get_trend_spending(self):
        query = """
        SELECT * 
        FROM ORDERS
        WHER E"""

    def get_mostpurchased_category(self):
        query = """
        SELECT Products
        """

    def generate_report(self):


class SustainabilityReport (self):
    def get_total_in_a_year(self):