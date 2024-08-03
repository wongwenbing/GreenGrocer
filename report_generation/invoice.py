import sys
sys.path.append('../GreenGrocer')
from db import db_connector

class Invoice:
    def __init__(self, invoice_id, invoice_date):
        self.invoice_id = invoice_id
        self.invoice_date = invoice_date

class InvoiceCustomer:
    def __init__(self):
        self.name = name
        self.email = email
        self.phonenumber = phone
        self.address = address
        self.datetime = ""
        self.total = ""

db, cursor = db_connector()

class Items:
    def __init__(self, items, prices, qtys):
        self.item = items
        self.price = prices
        self.qty = qtys
        self.total = self.price*self.qty

    def get_total(self):
        return self.total

    def info(self):
        return f"{self.item}, {self.price}, {self.qty}, {self.total}"

cust_info = "SELECT * From Customers"
cursor.execute(cust_info)
# rows = cursor.fetchall()
prod = """
SELECT p.usual_price, p.name, o.quantity
FROM Products p
INNER JOIN OrderDetails o
ON p.product_id = o.product_id
WHERE order_id = %s
"""

customer_id = 'OR101'
cursor.execute(prod, customer_id)
rows = cursor.fetchall()
for entry in rows:
    item = Items(entry['name'], entry['usual_price'], entry['quantity'])
    print(item.info())

