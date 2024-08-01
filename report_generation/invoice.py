import sys
sys.path.append('../GreenGrocer')
from db import db_connector
class InvoiceCustomer:
    def __init__(self):
        self.name = ""
        self.email = ""
        self.phonenumber = ""
        self.address = ""
        self.block = ""
        self.postal = ""
        self.datetime = ""
        self.total = ""

db, cursor = db_connector()

class Items:
    def __init__(self, items, prices, qtys):
        self.item = items
        self.price = prices
        self.qty = qtys
        self.total = self.price*self.qty

    def info(self):
        return f"{self.item}, {self.price}, {self.qty}, {self.total}"

cust_info = "SELECT * From Customers"
cursor.execute(cust_info)
rows = cursor.fetchall()
print(rows)



