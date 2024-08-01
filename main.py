from flask import Flask , render_template, request, redirect, url_for
from db import db_connector
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart
from report_generation.invoice import InvoiceCustomer, Items

app = Flask(__name__)

db,cursor = db_connector()

@app.route('/home')
def home(): 
    return render_template('custhome.html')

@app.route('/customer')
def customer_login(): 
    return render_template('customer.html')

@app.route('/staff')
def staff_login():
    return render_template('/staff.html')

@app.route('/nutritionn')
def view_nutrition(): 
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()
    nutrition_objects = [custnutrition(**entry) for entry in result]
    return render_template('nutritionsummary.html', count=len(nutrition_objects), customers = nutrition_objects)

@app.route('/')
def reports(): 
    graph_json = generate_pie_chart(cursor)

    return render_template('graphs.html', graph_json=graph_json)


@app.route('/invoice')
def invoicing():
    #fetch data from database
    cust_info = "SELECT * From Customers"
    cursor.execute(cust_info)
    rows = cursor.fetchall()
    #create object
    customer = InvoiceCustomer()
    customer_id = 1
    prod = """
    SELECT p.unit_price, p.name, o.qty
    FROM Products p
    INNER JOIN OrderDetails o
    ON p.product_id = o.product_id
    WHERE order_id = %s
    """
    cursor.execute(prod, customer_id)
    rows = cursor.fetchall()
    for entry in rows:
        Items(entry['name'], entry['unit_price'], entry['quantity'])
    print(rows)
    return render_template('invoice.html', products = products)


if __name__ == '__main__':
    app.run()
