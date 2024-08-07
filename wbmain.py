from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from db import db_connector
from datetime import datetime
from report_generation.nutritional_summary import custnutrition
from report_generation.invoice import Invoice, InvoiceCustomer, invoice_summary
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report, Retrieve_Customer_Report, Retrieve_Staff_Report
from report_generation.customer_report import PurchasingReport
from report_generation.staffreportgen import InventoryReport, SalesReport
import os
from xhtml2pdf import pisa
from io import BytesIO


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
    return redirect(url_for('cust_view_reports'))


@app.route('/cust_view_reports')
def cust_view_reports():
    #Fetch Data from db
    query = """SELECT * FROM Customer_Report WHERE customer_id = %s """
    cust_id = session.get('user_id')
    cursor.execute(query, cust_id)
    result = cursor.fetchall()
    print(result)
    reports = []
    for r in result:
        report = Retrieve_Customer_Report(r['cust_report_id'], r['customer_id'], r['coverage_start'], r['coverage_end'], r['report_type'])
        reports.append(report)
    return render_template('report_generation/reports_summary.html', reports=reports)


@app.route('/cust_retrieve_report', methods=['POST'])
def cust_retrieve_report():
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


@app.route('/cust_delete_report', methods=['POST'])
def cust_delete_report():
    report_id = request.form.get('report_id')
    query = """DELETE FROM Customer_Report WHERE cust_report_id = %s """
    cursor.execute(query, report_id)

    db.commit()

    return redirect(url_for('view_reports'))


@app.route('/cust_generate_report', methods=['GET', 'POST'])
def cust_generate_report():
    form = CustReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = customer_report(session['user_id'], form.start_date.data, form.end_date.data,
                                    form.type_of_report.data)
        session['cust_report_data'] = {
            'start_date': str(newreport.startdate),
            'end_date': str(newreport.end_date),
            'type_of_report': newreport.report_type
        }
        # For example, save the data or generate a report
        newreport.to_db()
        if newreport.report_type == "Purchasing":
            # Store the necessary data in session
            return redirect(url_for('purchasing_report'))
        elif newreport.report_type == "Sustainability":
            return redirect

        return redirect(url_for('success'))
    return render_template('report_generation/custreportgen.html', form=form)


@app.route('/purchasing_report')
def purchasing_report():
    report_data = session.get('cust_report_data')
    report = PurchasingReport(report_data['start_date'], report_data['end_date'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('report_generation/graphs.html', report=report)

@app.route('/cust_report_update', methods=['POST'])
def cust_update_report1():
    report_id = request.form.get('report_id')
    session['cust_report_id'] = report_id
    print(report_id)
    return redirect(url_for('cust_update_report2'))

@app.route('/cust_update_report', methods=['GET','POST'])
def cust_update_report2():
    update = CustReport(request.form)
    report_id = session['cust_report_id']
    if request.method == 'POST':
        report = customer_report(session['user_id'], update.start_date.data, update.end_date.data, update.type_of_report.data)
        query = """
        UPDATE Customer_Report
        SET customer_id = %s, coverage_start = %s, coverage_end = %s, report_type = %s
        WHERE cust_report_id = %s
        """
        statement = (report.custid, report.startdate, report.end_date, report.report_type, report_id)
        cursor.execute(query, statement)
        db.commit()
        return redirect(url_for('cust_view_reports'))
    else:
        query = "SELECT * FROM Customer_Report WHERE cust_report_id = %s"
        report_id = report_id
        print(report_id)
        cursor.execute(query, report_id)
        r = cursor.fetchone()
        report = Retrieve_Customer_Report(r['cust_report_id'], r['customer_id'], r['coverage_start'], r['coverage_end'],
                                       r['report_type'])
        update.start_date.data = datetime.strptime(report.start_date, '%Y-%m-%d')
        update.end_date.data = datetime.strptime(report.end_date, '%Y-%m-%d')
        update.type_of_report.data = report.report_type
        return render_template('report_generation/custupdatereport.html', form=update)

#STAFF
@app.route('/staff_generate_report', methods=['GET', 'POST'])
def staff_generate_report():
    form = StaffReport(request.form)
    if request.method == "POST" and form.validate():
        # Handle the form submission logic here
        newreport = staff_report(session['user_id'],form.start_date.data, form.end_date.data, form.type_of_report.data)
        print(newreport.info())
        session['staff_report_data'] = {
            'start_date': str(newreport.startdate),
            'end_date': str(newreport.end_date),
            'type_of_report': newreport.report_type
        }
        newreport.to_db()
        # For example, save the data or generate a report
        if newreport.report_type == "Inventory":
            # Store the necessary data in session
            return redirect(url_for('inventory_report'))
        elif newreport.report_type == "Sales":
            return redirect(url_for('sales_report'))
        elif newreport.report_type == "Category":
            return redirect(url_for('success'))
    return render_template('report_generation/staffreportgen.html', form=form)

@app.route('/staff_view_reports')
def staff_view_reports():
    #Fetch Data from db
    query = """SELECT * FROM Staff_Report WHERE staff_id = %s """
    staff_id = session.get('user_id')
    cursor.execute(query, staff_id)
    result = cursor.fetchall()
    print(result)
    reports = []
    for r in result:
        report = Retrieve_Staff_Report(r['staff_report_id'], r['staff_id'], r['coverage_start'], r['coverage_end'], r['report_type'])
        reports.append(report)
    return render_template('report_generation/staff_reports_summary.html', reports=reports)


@app.route('/staff_report_update', methods=['POST'])
def staff_update_report1():
    report_id = request.form.get('report_id')
    session['staff_report_id'] = report_id
    print(report_id)
    return redirect(url_for('staff_update_report2'))

@app.route('/staff_update_report', methods=['GET','POST'])
def staff_update_report2():
    update = StaffReport(request.form)
    report_id = session['staff_report_id']
    if request.method == 'POST':
        report = staff_report(session['user_id'], update.start_date.data, update.end_date.data, update.type_of_report.data)
        query = """
        UPDATE Staff_Report
        SET staff_id = %s, coverage_start = %s, coverage_end = %s, report_type = %s
        WHERE staff_report_id = %s
        """
        statement = (report.staffid, report.startdate, report.end_date, report.report_type, report_id)
        cursor.execute(query, statement)
        db.commit()
        return redirect(url_for('staff_view_reports'))
    else:
        query = "SELECT * FROM Staff_Report WHERE staff_report_id = %s"
        report_id = report_id
        print(report_id)
        cursor.execute(query, report_id)
        r = cursor.fetchone()
        report = Retrieve_Staff_Report(r['staff_report_id'], r['staff_id'], r['coverage_start'], r['coverage_end'],
                                       r['report_type'])
        update.start_date.data = datetime.strptime(report.start_date, '%Y-%m-%d')
        update.end_date.data = datetime.strptime(report.end_date, '%Y-%m-%d')
        update.type_of_report.data = report.report_type
        return render_template('report_generation/staffupdatereport.html', form=update)

@app.route('/inventory_report')
def inventory_report():
    # report_data = session.get('report_data')
    report = InventoryReport()
    report.get_totalinventoryvalue_bycategory()
    report.get_totalinventory()
    report.get_average_stock()
    return render_template('report_generation/inventory_report.html', report=report)


@app.route('/sales_report')
def sales_report():
    report_data = session.get('staff_report_data')
    report = SalesReport(report_data['start_date'], report_data['end_date'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('report_generation/graphs.html', report=report)


@app.route('/staff_retrieve_report', methods=['POST'])
def staff_retrieve_report():
    report_id = request.form.get('report_id')
    query = """SELECT * FROM Staff_Report WHERE staff_report_id = %s """
    cursor.execute(query, report_id)
    result = cursor.fetchone()
    session['report_data'] = {
        'start_date': result['coverage_start'],
        'end_date': result['coverage_end'],
        'type_of_report': result['report_type']
    }
    if result['report_type'] == "Purchasing":
        return redirect(url_for('purchasing_report'))


@app.route('/staff_delete_report', methods=['POST'])
def staff_delete_report():
    report_id = request.form.get('report_id')
    print(report_id)
    query = """DELETE FROM Staff_Report WHERE staff_report_id = %s """
    cursor.execute(query, report_id)

    db.commit()

    return redirect(url_for('staff_view_reports'))


@app.route('/print_invoice', methods=['POST'])
def print_invoice():
    invoice_id = request.form.get('invoice_id')
    query = """
        SELECT i.ID, i.Invoiced_date, i.order_id, i.user_id, u.name, u.email, u.phone_number, u.address
        FROM Invoice i INNER JOIN users u
        ON i.user_id = u.id
        WHERE i.ID = %s
        """
    cursor.execute(query, invoice_id)
    row = cursor.fetchone()
    print(row)
    invoice = InvoiceCustomer(row['ID'], row['Invoiced_date'], row['order_id'], row['name'],
                              row['email'], row['phone_number'], row['address'])
    invoice_summary(invoice)
    products = invoice.products
    html = render_template('report_generation/print_invoices.html', invoice=invoice,
                           products=products)
    filename = f"Invoice#{invoice_id}.pdf"
    pdf_output = BytesIO()

    pisa.CreatePDF(html, dest=pdf_output, encoding='utf-8')
    pdf_output.seek(0)
    return send_file(pdf_output,as_attachment=True, mimetype='application/pdf', download_name=filename)


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




@app.route('/success')
def success():
    return "Report generated successfully!"


if __name__ == '__main__':
    app.run()
