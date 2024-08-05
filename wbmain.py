from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import db_connector
from report_generation.nutritional_summary import custnutrition
from report_generation.invoice import Invoice, InvoiceCustomer, invoice_summary
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report, Retrieve_Customer_Report
from report_generation.customer_report import PurchasingReport
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)  # Generates a random secret key each time

db, cursor = db_connector()
print(db, cursor)

# Insert Report Generaation here

@app.route('/')
def index():
    # Set session data in a route where a request context is active
    session['user_id'] = 1
    print(session['user_id'])
    return redirect(url_for('view_invoice'))

@app.route('/nutrition')
def view_nutrition():
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()
    nutrition_objects = [custnutrition(**entry) for entry in result]
    return render_template('report_generation/nutritionsummary.html', count=len(nutrition_objects), customers=nutrition_objects)

@app.route('/view_reports')
def view_reports():
    #Fetch Data from db
    query = """SELECT * FROM Customer_Report WHERE customer_id = %s """
    cust_id = session.get('user_id')
    print(cust_id)
    cursor.execute(query, cust_id)
    result = cursor.fetchall()
    reports = []
    for r in result:
        report = Retrieve_Customer_Report(r['cust_report_id'], r['customer_id'], r['coverage_start'], r['coverage_end'], r['report_type'])
        reports.append(report)
    return render_template('report_generation/reports_summary.html', reports=reports)

@app.route('/retrieve_report', methods=['POST'])
def retrieve_report():
    report_id = request.form.get('report_id')
    query = """SELECT * FROM Customer_Report WHERE cust_report_id = %s """
    cursor.execute(query, report_id)
    result = cursor.fetchone()
    session['report_data'] = {
        'start_date': result['coverage_start'],
        'end_date': result['coverage_end'],
        'type_of_report': result['report_type']
    }
    if result['report_type'] == "Purchasing":
        return redirect(url_for('purchasing_report'))

@app.route('/purchasing_report')
def purchasing_report():
    report_data = session.get('report_data')
    report = PurchasingReport(report_data['start_date'], report_data['end_date'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('report_generation/graphs.html', report=report)



@app.route('/view_invoices')
def view_invoice():
    cust_id = session['user_id']
    query = "SELECT * FROM Invoice WHERE user_id = %s"
    cursor.execute(query, cust_id)
    rows = cursor.fetchall()
    invoices = []
    for row in rows:
        invoice = Invoice(row['ID'], row['Invoiced_date'], row['order_id'])
        invoice_summary(invoice)
        invoices.append(invoice)
    return render_template('report_generation/invoice_summary.html', invoices=invoices)


@app.route('/retrieve_invoice', methods=['POST'])
def retrieve_invoice():
    invoice_id = request.form.get('invoice_id')
    query = "SELECT * FROM Invoice WHERE ID = %s"
    cursor.execute(query, invoice_id)
    row = cursor.fetchone()
    invoice = Invoice(row['ID'], row['Invoiced_date'], row['order_id'])
    session['invoice'] = invoice_id
    return redirect(url_for('invoicing'))


@app.route('/invoice')
def invoicing():
    invoice_data = session.get('invoice')
    query = """
    SELECT i.ID, i.Invoiced_date, i.order_id, i.user_id, u.name, u.email, u.phone_number, u.address
    FROM Invoice i INNER JOIN users u
    ON i.user_id = u.id
    WHERE i.ID = %s
    """
    cursor.execute(query, invoice_data)
    row = cursor.fetchone()
    print(row)
    invoice = InvoiceCustomer(row['ID'], row['Invoiced_date'], row['order_id'], row['name'],
                              row['email'], row['phone_number'], row['address'])
    invoice_summary(invoice)
    products = invoice.products
    return render_template('report_generation/invoice.html', invoice=invoice,
                           products=products)


@app.route('/cust/generate_report/', methods=['GET', 'POST'])
def cust_generate_report():
    form = CustReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = customer_report(form.start_date.data, form.end_date.data,
                                    form.type_of_report.data)
        session['report_data'] = {
            'start_date': str(newreport.startdate),
            'end_date': str(newreport.end_date),
            'type_of_report': newreport.report_type
        }
        # For example, save the data or generate a report
        if newreport.report_type == "Purchases":
            # Store the necessary data in session
            return redirect(url_for('purchasing_report'))
        elif newreport.report_type == "Sustainability":
            return redirect
        return redirect(url_for('success'))
    return render_template('report_generation/custreportgen.html', form=form)


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
