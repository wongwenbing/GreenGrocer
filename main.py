from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import db_connector
import pymysql
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart
from report_generation.invoice import InvoiceCustomer, Items
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report
from db import db_connector
from account_management.forms import CreateUserForm


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

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db, c = db_connector()
        c.execute('SELECT * FROM users WHERE email = %s', (email))
        user = c.fetchone()
        db.close()
        
        if user and user['password'] == password:
            session['id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login_bootstrap.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        password = request.form['password']
        
        # Log the form data for debugging
        print(f"Received signup data: {name}, {email}, {phone_number}, {address}, {date_of_birth}, {password}")
        
        if not email or not password:
            flash('Email and Password are required fields.', 'danger')
            return render_template('signup_bootstrap.html')

        try:
            db, c = db_connector()
            c.execute('''
                INSERT INTO users (name, email, phone_number, address, date_of_birth, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, email, phone_number, address, date_of_birth, password))
            db.commit()
            flash('Account created successfully! Please login.', 'success')
            print('success')
            return redirect(url_for('login'))
        except pymysql.IntegrityError:
            flash('Email already registered.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            db.close()
    return render_template('signup_bootstrap.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'id' not in session:
        flash('You are not logged in!', 'danger')
        return redirect(url_for('login'))
    
    id = session['id']
    db, c = db_connector()

    if request.method == 'POST':
        if 'delete_account' in request.form:
            c.execute('DELETE FROM users WHERE id = %s', (id))
            db.commit()
            db.close()
            session.pop('id', None)
            flash('Account deleted successfully!', 'success')
            return redirect(url_for('signup'))
        else:
            name = request.form['name']
            email  = request.form['email']
            phone_number = request.form['phone_number']
            address = request.form['address']
            date_of_birth = request.form['date_of_birth']
            val = (name, email , phone_number, address, date_of_birth, id)
            query = """
UPDATE users
SET name = %s, email  = %s, phone_number = %s, address = %s, date_of_birth = %s
WHERE id = %s
"""
            c.execute(query, val)
            db.commit()
            flash('Profile updated successfully!', 'success')
    
    c.execute('SELECT * FROM users WHERE id = %s', (id))
    user = c.fetchone()
    db.close()
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))




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


@app.route('/staffreport', methods=['GET', 'POST'])
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
