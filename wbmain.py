from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
from db import db_connector
from datetime import datetime
from report_generation.invoice import Invoice, InvoiceCustomer, invoice_summary
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report, Retrieve_Customer_Report, Retrieve_Staff_Report
from report_generation.customer_report import PurchasingReport, SustainabilityReport
from report_generation.staffreportgen import InventoryReport, SalesReport
import os
from xhtml2pdf import pisa
from io import BytesIO, StringIO
import io
import pandas as pd
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText



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
    return redirect(url_for('view_invoices'))


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
    print(session)
    session['cust_report_data'] = {
        'start_date': result['coverage_start'],
        'end_date': result['coverage_end'],
        'type_of_report': result['report_type']
    }
    if result['report_type'] == 'Purchasing':
        return redirect(url_for('purchasing_report'))
    elif result['report_type'] == 'Sustainability':
        return redirect(url_for('sustainability_report'))
    else:
        return redirect(url_for("success"))


@app.route('/cust_delete_report', methods=['POST'])
def cust_delete_report():
    report_id = request.form.get('report_id')
    query = """DELETE FROM Customer_Report WHERE cust_report_id = %s """
    cursor.execute(query, report_id)

    db.commit()

    return redirect(url_for('cust_view_reports'))


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
            return redirect(url_for('sustainability_report'))
        else:
            return redirect(url_for('success'))
    return render_template('report_generation/custreportgen.html', form=form)


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


@app.route('/purchasing_report')
def purchasing_report():
    report_data = session.get('cust_report_data')
    report = PurchasingReport(report_data['start_date'], report_data['end_date'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('report_generation/graphs.html', report=report)


@app.route('/sustainability_report')
def sustainability_report():
    report_data = session.get('cust_report_data')
    cust_id = session['user_id']
    report = SustainabilityReport(cust_id, report_data['start_date'], report_data['end_date'])
    report.carbon_emissions()
    report.graph_organic()
    report.line_carbonemissions()
    return render_template('report_generation/sustainability_report.html', report=report)



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

@app.route('/download_inventory_report')
def download_inventory_report():
    query = """
    SELECT p.name, i.stock_quantity, i.reorder_level, s.stock_status
    FROM Inventory i
    INNER JOIN Products p ON i.product_id = p.product_id
    INNER JOIN StockStatus s ON i.stock_status_id = s.stock_status_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    rows = pd.DataFrame(rows)
    # Convert DataFrame to CSV
    output = StringIO()
    rows.to_csv(output, index=False)
    output.seek(0)

    # Create a response object and set headers
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=inventory_report.csv"}
    )

    EMAIL_ADDRESS = 'staff.greengrocerr@gmail.com'
    EMAIL_PASSWORD = 'fjad oapl nsac lkfa'

    msg = EmailMessage()
    msg['Subject'] = 'Report Generated Successfully!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'aniskyguy331@gmail.com'
    msg.set_content('This is to inform you that the Inventory report has been generated successfully.')

    msg.add_attachment(output.getvalue(),
                       maintype='application',
                       subtype='csv',
                       filename='Inventory_Report.csv')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    return response


@app.route('/sales_report')
def sales_report():
    report_data = session.get('staff_report_data')
    report = SalesReport(report_data['start_date'], report_data['end_date'])
    print(report.get_info())
    report.get_average_order_spending()
    report.get_total_amount()
    report.get_mostpurchased_category()
    return render_template('report_generation/salesgraphs.html', report=report)

@app.route('/download_sales_report', methods=['POST'])
def download_sales_report():
    startdate = str(request.form.get('startdate'))
    enddate = str(request.form.get('enddate'))
    string = (startdate, enddate)

    # Create a BytesIO buffer to hold the Excel file in memory
    output = BytesIO()

    # Database queries
    # Query 1: Sales by Category
    query1 = """
            SELECT od.quantity, c.category_name
            FROM OrderDetails od
            INNER JOIN Products p ON od.product_id = p.product_id
            INNER JOIN Categories c ON p.category_id = c.category_id
            INNER JOIN Orders o ON od.order_id = o.order_id
            WHERE o.datetime BETWEEN %s AND %s
        """
    cursor.execute(query1, string)
    rows = cursor.fetchall()
    df1 = pd.DataFrame(rows, columns=['quantity', 'category_name'])
    df1 = df1.groupby('category_name', as_index=False)['quantity'].sum()
    df1 = df1.sort_values(by=['quantity'], ascending=False)
    df1 = df1.reset_index(drop=True)

    # Query 2: Sales by Product
    query2 = """
            SELECT od.quantity, p.name
            FROM OrderDetails od
            INNER JOIN Products p ON od.product_id = p.product_id
            INNER JOIN Orders o ON od.order_id = o.order_id
            WHERE o.datetime BETWEEN %s AND %s
        """
    cursor.execute(query2, string)
    rows = cursor.fetchall()
    df2 = pd.DataFrame(rows, columns=['quantity', 'product_name'])
    df2 = df2.groupby('product_name', as_index=False)['quantity'].sum()
    df2 = df2.sort_values(by=['quantity'], ascending=False)
    df2 = df2.reset_index(drop=True)

    # Query 3: Sales by Order
    query3 = """
            SELECT o.order_id, SUM(od.quantity * p.usual_price) AS sales
            FROM OrderDetails od
            INNER JOIN Products p ON od.product_id = p.product_id
            INNER JOIN Orders o ON od.order_id = o.order_id
            WHERE o.datetime BETWEEN %s AND %s
            GROUP BY o.order_id
        """
    cursor.execute(query3, string)
    rows = cursor.fetchall()
    df3 = pd.DataFrame(rows, columns=['order_id', 'sales'])
    df3 = df3.reset_index(drop=True)

    # Write DataFrames to the BytesIO buffer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Sales by Category', index=False)
        df2.to_excel(writer, sheet_name='Sales by Product', index=False)
        df3.to_excel(writer, sheet_name='Sales by Order', index=False)

    # Seek to the beginning of the BytesIO buffer
    output.seek(0)

    EMAIL_ADDRESS = 'staff.greengrocerr@gmail.com'
    EMAIL_PASSWORD = 'fjad oapl nsac lkfa'

    msg = EmailMessage()
    msg['Subject'] = 'Sales Report Generated Successfully!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'aniskyguy331@gmail.com'
    msg.set_content("""
    Hi, 
    
    This is to inform you that the Sales Report has been generated successfully. 
    
    Do refer to the attached.
    
    Regards, 
    GreenGrocer Team
    """)

    msg.add_attachment(output.getvalue(),
                       maintype='application',
                       subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                       filename='SalesReport.xlsx')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


    # Send the file to the client
    return send_file(
        output,
        as_attachment=True,
        download_name='SalesReport.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/staff_retrieve_report', methods=['POST'])
def staff_retrieve_report():
    report_id = request.form.get('report_id')
    query = """SELECT * FROM Staff_Report WHERE staff_report_id = %s """
    cursor.execute(query, report_id)
    result = cursor.fetchone()
    session['staff_report_data'] = {
        'start_date': result['coverage_start'],
        'end_date': result['coverage_end'],
        'type_of_report': result['report_type']
    }
    if result['report_type'] == "Sales":
        return redirect(url_for('sales_report'))
    elif result['report_type'] == "Inventory":
        return redirect(url_for('inventory_report'))


@app.route('/staff_delete_report', methods=['POST'])
def staff_delete_report():
    report_id = request.form.get('report_id')
    print(report_id)
    query = """DELETE FROM Staff_Report WHERE staff_report_id = %s """
    cursor.execute(query, report_id)

    db.commit()

    return redirect(url_for('staff_view_reports'))

@app.route('/view_invoices')
def view_invoices():
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


@app.route('/email_invoice', methods=['POST'])
def email_invoice():
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

    EMAIL_ADDRESS = 'staff.greengrocerr@gmail.com'
    EMAIL_PASSWORD = 'fjad oapl nsac lkfa'

    msg = EmailMessage()
    msg['Subject'] = f'Your Invoice#{invoice_id} is Ready!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'aniskyguy331@gmail.com'
    msg.set_content("""
    Hi, 

    This is to inform you that your recent purchase has been invoiced.

    Do refer to the attached.
    
    We look forward to your purchases again!

    Regards, 
    GreenGrocer Team
    """)

    msg.add_attachment(pdf_output.getvalue(),
                   maintype='application',
                   subtype='pdf',
                   filename=f'Invoice#{invoice_id}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

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
