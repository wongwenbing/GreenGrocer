from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import db_connector
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart
from report_generation.invoice import InvoiceCustomer, Items
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report
from report_generation.customer_report import PurchasingReport
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)  # Generates a random secret key each time

db, cursor = db_connector()


# Insert Report Generaation here
@app.route('/nutrition')
def view_nutrition():
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()
    nutrition_objects = [custnutrition(**entry) for entry in result]
    return render_template('nutritionsummary.html', count=len(nutrition_objects), customers=nutrition_objects)


@app.route('/graphs')
def reports():
    report_data = session.get('report_data')
    report = PurchasingReport(report_data['start_date'], report_data['end_date'],
                            report_data['description'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('graphs.html', report=report)


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


@app.route('/', methods=['GET', 'POST'])
def cust_generate_report():
    form = CustReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = customer_report(form.start_date.data, form.end_date.data, form.description.data,
                                    form.type_of_report.data)
        print(newreport.info())
        # For example, save the data or generate a report
        if newreport.report_type == "Purchases":
            # Store the necessary data in session
            session['report_data'] = {
                'start_date': str(newreport.startdate),
                'end_date': str(newreport.end_date),
                'description': newreport.report_type,
                'type_of_report': newreport.report_type
            }
            print(session)
            return redirect(url_for('reports'))
        return redirect(url_for('success'))
    return render_template('custreportgen.html', form=form)


@app.route('/staffreport', methods=['GET', 'POST'])
def staff_generate_report():
    form = StaffReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = staff_report(form.start_date.data, form.end_date.data, form.description.data,
                                 form.type_of_report.data)
        print(newreport.info())
        # For example, save the data or generate a report
        return redirect(url_for('success'))
    return render_template('custreportgen.html', form=form)


@app.route('/success')
def success():
    return "Report generated successfully!"


if __name__ == '__main__':
    app.run()
