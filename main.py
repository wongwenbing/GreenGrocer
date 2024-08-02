from flask import Flask, render_template, request, redirect, url_for
from db import db_connector
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart
from report_generation.invoice import InvoiceCustomer, Items
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report

app = Flask(__name__)

db, cursor = db_connector()


@app.route('/home')
def home():
    return render_template('custhome.html')


@app.route('/customer')
def customer_login():
    return render_template('customer.html')


@app.route('/staff')
def staff_login():
    return render_template('/staff.html')

#Insert Account Generation here





#Insert Transaction Processing here





#Insert Customer Support Herre





#Insert Report Generaation here
@app.route('/nutritionn')
def view_nutrition():
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()
    nutrition_objects = [custnutrition(**entry) for entry in result]
    return render_template('nutritionsummary.html', count=len(nutrition_objects), customers=nutrition_objects)


@app.route('/reports')
def reports():
    graph_json = generate_pie_chart(cursor)

    return render_template('graphs.html', graph_json=graph_json)


@app.route('/invoice')
def invoicing():
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
    products = []
    total = 0
    for entry in rows:
        item = Items(entry['name'], entry['usual_price'], entry['quantity'])
        products.append(item)
        print(item.info())
    total = float(sum(item.get_total() for item in products))
    gst = float(0.09) * total
    grandtotal = gst + total
    return render_template('invoice.html', products=products, subtotal=total, gst=gst, grandtotal=grandtotal)


@app.route('/customer/reportgen', methods=['GET', 'POST'])
def cust_generate_report():
    form = CustReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = customer_report(form.start_date.data, form.end_date.data, form.description.data, form.type_of_report.data)
        print(newreport.info())
        # For example, save the data or generate a report
        return redirect(url_for('success'))
    return render_template('custreportgen.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def staff_generate_report():
    form = StaffReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = staff_report(form.start_date.data, form.end_date.data, form.description.data, form.type_of_report.data)
        print(newreport.info())
        # For example, save the data or generate a report
        return redirect(url_for('success'))
    return render_template('custreportgen.html', form=form)

@app.route('/success')
def success():
    return "Report generated successfully!"


if __name__ == '__main__':
    app.run()
