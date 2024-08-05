import sys
sys.path.append('../GreenGrocer')
from db import db_connector

class Invoice:
    def __init__(self, invoice_id, invoice_date, order_id):
        self.invoice_id = invoice_id
        self.invoice_date = invoice_date
        self.order_id = order_id
        self.subtotal = ""
        self.gst = ""
        self.grandtotal = ""
        self.products = ""
    def set_subtotal(self, total):
        self.subtotal = total
    def set_gst(self,gst):
        self.gst = gst
    def set_grand_total(self, grandtotal):
        self.grandtotal = grandtotal
    def set_products(self, products):
        self.products = products

class InvoiceCustomer(Invoice):
    def __init__(self, invoice_id, invoice_date, order_id, name, email, phonenumber, address):
        super().__init__(invoice_id, invoice_date, order_id)
        self.name = name
        self.email = email
        self.phonenumber = phonenumber
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


def invoice_summary(invoice):
    products = []
    prod = """
            SELECT p.usual_price, p.name, o.quantity
            FROM Products p
            INNER JOIN OrderDetails o
            ON p.product_id = o.product_id
            WHERE order_id = %s
            """
    order_id = invoice.order_id
    cursor.execute(prod, order_id)
    rows = cursor.fetchall()
    for entry in rows:
        item = Items(entry['name'], entry['usual_price'], entry['quantity'])
        products.append(item)
        print(item.info())
    total = float(sum(item.get_total() for item in products))
    gst = float(0.09) * total
    grandtotal = gst + total
    invoice.set_subtotal(total)
    invoice.set_gst(gst)
    invoice.set_grand_total(grandtotal)
    invoice.set_products(products)