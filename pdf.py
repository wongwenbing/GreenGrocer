from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from db import db_connector
from report_generation.invoice import Invoice, InvoiceCustomer, invoice_summary
import os
import asyncio
from xhtml2pdf import pisa
from io import BytesIO

db, cursor = db_connector()
invoice_id = 8001
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
with open("templates/report_generation/print_invoice.html", 'r', encoding='utf-8') as file:
    html = file.read()
filename = f"Invoice#{invoice_id}.pdf"

pdf_output = BytesIO()

pisa.CreatePDF(html, dest=pdf_output, encoding='utf-8')

with open("html-file-to-pdf.pdf", "wb") as pdf_file:
    # Write the PDF content to the file
    pdf_file.write(pdf_output.getvalue())

# async with async_playwright() as p:
#     browser = await p.chromium.launch()
#     page = await browser.new_page()
#     await page.set_content(html)
#     await page.pdf(path=filename)
#     await browser.close()
# return send_file(f"static/{filename}", mimetype='application/pdf', as_attachment=True)
