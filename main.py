from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, Response

from customer_support.flaskStaff import sanitize_email
from db import db_connector
import pymysql
from datetime import datetime
from report_generation.nutritional_summary import custnutrition
from report_generation.invoice import Invoice, InvoiceCustomer, invoice_summary
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report, Retrieve_Customer_Report, Retrieve_Staff_Report
from report_generation.customer_report import PurchasingReport, SustainabilityReport
from report_generation.staffreportgen import InventoryReport, SalesReport
import os
from werkzeug.security import generate_password_hash, check_password_hash
from customer_support.forms import TicketForm
from customer_support.faqclass import FAQ
from account_management.forms import RegistrationForm, CreateUserForm
# from xhtml2pdf import pisa
from io import BytesIO, StringIO
import io
import pandas as pd
import smtplib
from email.message import EmailMessage
from transaction_processing.dao import DAO
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key each time


db, cursor = db_connector()

# @app.route('/')
# def index():
#     # Set session data in a route where a request context is active
#     session['user_id'] = 1
#     print(session['user_id'])
#     return redirect(url_for('staff_view_reports'))
#

@app.route('/')
def home():
    session['user_id'] = 1
    return render_template('base_browse.html')

@app.route('/customer')
def customer_login():
    return render_template('account_management/signup_bootstrap.html')

@app.route('/staff')
def staff_login():
    return render_template('staff.html')


# Insert Account Generation here
# Login, Sign up, Profile
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = str(request.form['email'])
        password = request.form['password']
        db, cursor = db_connector()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email))
        user = cursor.fetchone()

        if not user:
            db, cursor = db_connector()
            cursor.execute('SELECT * FROM staff WHERE email = %s', (email))
            user = cursor.fetchone()
            role = 'staff' if user else None
        else:
            role = 'users'

        db.close()
        if user and check_password_hash(user['password'], password):
            session['id'] = user['id']
            session['name'] = user['name']
            session['role'] = role
            flash('Logged in successfully!', 'success')
            if role == 'users':
                return redirect(url_for('products'))
            return redirect(url_for('profile'))



        else:
            flash('Invalid email or password', 'danger')
   
    return render_template('account_management/login_bootstrap.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
   
    if request.method == "POST" and form.validate():
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        # Log the form data for debugging
        print(f"Received signup data: {name}, {email}, {phone_number}, {address}, {date_of_birth}, {password}")
        
        if not email or not password:
            flash('Email and Password are required fields.', 'danger')
            return render_template('signup_bootstrap.html', form=form)

        try:
            db, cursor = db_connector()
            cursor.execute('''
                INSERT INTO users (name, email, phone_number, address, date_of_birth, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, email, phone_number, address, date_of_birth, hashed_password))
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
    else:
        errors = []
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field.capitalize()}: {error}")
        return render_template('account_management/signup_bootstrap.html', form=form, errors=" ".join(errors))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'id' not in session:
        flash('You are not logged in!', 'danger')
        return redirect(url_for('login'))
   
    id = session['id']
    role = session['role']

    if request.method == 'POST':
        if 'delete_account' in request.form:
            db, cursor = db_connector()
            cursor.execute(f'DELETE FROM {role} WHERE id = %s', (id))
            db.commit()
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
            query = f"""
UPDATE {role}
SET name = %s, email = %s, phone_number = %s, address = %s, date_of_birth = %s
WHERE id = %s
"""
            db, cursor = db_connector()
            cursor.execute(query, val)
            db.commit()
            flash('Profile updated successfully!', 'success')
    db, cursor = db_connector()
    cursor.execute(f'SELECT * FROM {role} WHERE id = %s', (id))
    user = cursor.fetchone()
    db.close()
   
    return render_template('account_management/profile.html', user=user)



@app.route('/logout')
def logout():
    for x in list(session.keys()):
            session.pop(x, None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


# Staff assist with customer account (Create)
@app.route('/createCustomers', methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm(request.form)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        default_password = "P@ssw0rd"

        try:
            db, cursor = db_connector()
            cursor.execute('''
                INSERT INTO users (name, email, phone_number, address, date_of_birth, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, email, phone_number, address, date_of_birth, default_password))
            db.commit()
           
            flash('Account created successfully!', 'success')
        except pymysql.IntegrityError:
            flash('Email already registered.', 'danger')

        finally:
            db.close()

        return redirect(url_for('retrieve_customers'))
    return render_template('account_management/createCustomers.html', form=form)


# Staff assist with customer account (Retrieve)
@app.route('/retrieveCustomers')
def retrieve_customers():
    db, cursor = db_connector()
    cursor.execute('SELECT id, name, email, phone_number, address, date_of_birth FROM users')

    users = cursor.fetchall()
    db.close()
    return render_template('account_management/retrieveCustomers.html', count=len(users), users_list=users)

# Staff assist with customer account (Update)
@app.route('/updateUser/<id>/', methods=['GET', 'POST'])
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        val = (name, email, phone_number, address, date_of_birth, id)
        query = """
UPDATE users
SET name = %s, email = %s, phone_number = %s, address = %s, date_of_birth = %s
WHERE id = %s
"""
        db, cursor = db_connector()
        cursor.execute(query, val)
        db.commit()

        flash('Profile updated successfully!', 'success')

        return redirect(url_for('retrieve_customers'))
    else:
        db, cursor = db_connector()
        cursor.execute('SELECT * FROM users WHERE id = %s', (id))
        user = cursor.fetchone()
        db.close()

        update_user_form.name.data = user['name']
        update_user_form.email.data = user['email']
        update_user_form.phone_number.data = user['phone_number']
        update_user_form.address.data = user['address']
        update_user_form.date_of_birth.data = user['date_of_birth']

        return render_template('account_management/updateCustomers.html', form=update_user_form)


# Staff assist with customer account (Delete)
@app.route('/deleteUser/<id>', methods=['POST'])
def delete_user(id):
    db, cursor = db_connector()
    cursor.execute('DELETE FROM users WHERE id = %s', (id))
    db.commit()
    db.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('retrieve_customers'))



#Insert Transaction Processing here

dao = DAO()
@app.route('/products')
def products():
    search_query = request.args.get('search', '')
    category_id = request.args.get('category_id')
    # Ensure `products` is always defined
    products = []

    try:
        if category_id:
            # Fetch products based on category ID only
            products = dao.get_products_by_category(category_id)
        elif search_query:
            # Fetch products based on search query only
            products = dao.get_products_by_search(search_query)
        else:
            # Fetch all active products if no search query or category ID is provided
            products = dao.get_all_products(status_filter='active')
    except Exception as e:
        print(f"Error fetching products: {e}")
        products = dao.get_all_products(status_filter='active')  # Fallback to active products if an error occurs

    # Fetch category names for breadcrumb
    categories = dao.get_all_categories()

    selected_category_name = None
    parent_category_name = None

    if category_id:
        selected_category = next((cat for cat in categories if cat['category_id'] == category_id), None)
        if selected_category:
            selected_category_name = selected_category['category_name']
            parent_category = next((cat for cat in categories if cat['category_id'] == selected_category.get('parent_id')), None)
            if parent_category:
                parent_category_name = parent_category['category_name']

    return render_template('transaction_processing/index.html', products=products, categories=categories,
                           selected_category_name=selected_category_name,
                           parent_category_name=parent_category_name)


@app.route('/product/<product_id>')
def product_detail(product_id):
    product = dao.get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products'))

    category_id = product['category_id']
    featured_products = dao.get_products_by_category(category_id)

    return render_template('transaction_processing/product_detail.html', product=product, featured_products=featured_products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    customer_id = request.form['customer_id']
    quantity = request.form['quantity']
    dao.add_product_to_cart(customer_id, product_id, quantity)
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    customer_id = request.args.get('customer_id', '1')  # For simplicity, hardcoded customer_id
    cart_items = dao.get_cart_by_customer_id(customer_id)
    return render_template('transaction_processing/cart.html', cart_items=cart_items, customer_id=customer_id)

@app.route('/update_cart_item/<product_id>', methods=['POST'])
def update_cart_item(product_id):
    customer_id = request.form['customer_id']
    quantity = int(request.form['quantity'])

    dao.update_cart_item(customer_id, product_id, quantity)

    return redirect(url_for('view_cart'))

@app.route('/delete_cart_item/<product_id>', methods=['POST'])
def delete_cart_item(product_id):
    customer_id = request.form['customer_id']

    dao.delete_cart_item(customer_id, product_id)

    return redirect(url_for('view_cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    customer_id = request.form['customer_id']

    dao.clear_cart(customer_id)

    return redirect(url_for('view_cart'))

@app.route('/admin_products', methods=['GET'])
def admin_products():
    status_filter = request.args.get('status')  # Get filter from request
    
    if status_filter not in ['active', 'drafts', 'archive', None]:
        status_filter = None  # Default to showing all products if the status filter is invalid

    products = dao.get_all_products(status_filter=status_filter)
    
    # Debug: Print or log the products and status filter
    print(f"Status Filter: {status_filter}")
    print(f"Products: {products}")

    # Get totals
    total_all = dao.get_total_products()
    total_active = dao.count_products_by_status('active')
    total_drafts = dao.count_products_by_status('drafts')
    total_archive = dao.count_products_by_status('archive')
    return render_template('/transaction_processing/admin_products.html', products=products, status_filter=status_filter,total_all=total_all,
        total_active=total_active,
        total_drafts=total_drafts,
        total_archive=total_archive)


@app.route('/admin_product/<product_id>')
def admin_product_detail(product_id):
    product = dao.get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))
    return render_template('transaction_processing/admin_product_detail.html', product=product)

## Admin add product
@app.route('/admin_add_product', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        category_id = request.form.get('category_id')
        supplier_id = request.form.get('supplier_id')
        name = request.form.get('name')
        uom = request.form.get('uom')
        price = request.form.get('price')
        country_of_origin = request.form.get('country_of_origin')
        eco_info = request.form.get('eco_info')
        ingredients = request.form.get('ingredients')
        tags = request.form.get('tags')
        discount_id = request.form.get('discount_id')
        status = request.form.get('status')  # Added status field

        if not product_id or not name or not uom:
            flash('Missing required fields', 'danger')
            return redirect(url_for('admin_add_product'))

        try:
            price = float(price)
        except ValueError:
            flash('Invalid price format', 'danger')
            return redirect(url_for('admin_add_product'))

        try:
            dao.create_product(
                product_id, category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status
            )
            flash('Product added successfully', 'success')
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')

        return redirect(url_for('admin_products'))

    categories = dao.get_all_categories()
    suppliers = dao.get_all_suppliers()
    discounts = dao.get_all_discounts_from_products()

    return render_template('transaction_processing/admin_add_product.html', categories=categories, suppliers=suppliers, discounts=discounts)



@app.route('/admin/edit_product/<product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    # Fetch the existing product data
    product = dao.get_product_by_id(product_id)
    
    if request.method == 'POST':
        # Retrieve and convert form data
        category_id = request.form.get('category_id')
        supplier_id = request.form.get('supplier_id')
        name = request.form.get('name')
        uom = request.form.get('uom')
        price_str = request.form.get('usual_price')  # Make sure this matches the form field name
        country_of_origin = request.form.get('country_of_origin')
        eco_info = request.form.get('eco_info')
        ingredients = request.form.get('ingredients')
        tags = request.form.get('tags')
        discount_id = request.form.get('discount_id')
        status = request.form.get('status')

        # Use existing values if the form field is empty
        category_id = category_id if category_id else product['category_id']
        supplier_id = supplier_id if supplier_id else product['supplier_id']
        name = name if name else product['name']
        uom = uom if uom else product['uom']

        # Convert price to Decimal
        try:
            price = Decimal(price_str) if price_str else Decimal(product['usual_price'])
        except (ValueError, InvalidOperation):
            flash('Invalid price format', 'danger')
            return redirect(url_for('admin_edit_product', product_id=product_id))
        
        country_of_origin = country_of_origin if country_of_origin else product['country_of_origin']
        eco_info = eco_info if eco_info else product['eco_info']
        ingredients = ingredients if ingredients else product['ingredients']
        tags = tags if tags else product['tags']
        discount_id = discount_id if discount_id else product['discount_id']
        status = status if status else product['status']

        # Perform the update
        try:
            dao.update_product(
                product_id, category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status
            )
            flash('Product updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'danger')

        return redirect(url_for('admin_products'))

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))

    # Fetch other data needed for the form (categories, suppliers, etc.)
    categories = dao.get_all_categories()
    suppliers = dao.get_all_suppliers()
    discounts = dao.get_all_discounts_from_products()
    uoms = ['kg', 'g', 'l', 'ml', 'pcs']

    return render_template('/transaction_processing/admin_edit_product.html', product=product, categories=categories, suppliers=suppliers, discounts=discounts, uoms=uoms)


@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def admin_delete_product(product_id):
    dao.delete_product(product_id)
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))


#Insert Customer Support Herre
@app.route('/pages-contact')
def contact_us():
    return render_template('customer_support/pages-contact.html')


@app.route('/faq')
def faq():
    faq_objects = []
    connection = None
    try:
        db, cursor = db_connector()
        if db is None:
            raise Exception("Failed to establish a database connection.")

        with cursor:
            cursor.execute("SELECT question, answer FROM FAQs LIMIT 10")
            faqs = cursor.fetchall()
            if not faqs:
                print("No FAQs found in the database.")
            for faq in faqs:
                faq_obj = FAQ(faq['question'], faq['answer'])
                faq_objects.append(faq_obj)
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if db:
            db.close()

    return render_template('customer_support/pages-faq.html', faqs=faq_objects)


@app.route('/create_ticket', methods=['GET', 'POST'])
def raise_a_ticket():
    form = TicketForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']
        issue = request.form['issue']
        topic = request.form['topic']

        # db, cursor = db_connector()
        cursor.execute(
            'INSERT INTO tickets (username, email, date, time, issue, topic) VALUES (%s, %s, %s, %s, %s, %s)',
            (username, email, date, time, issue, topic)
        )
        db.commit()
        db.close()
    return render_template('customer_support/create_ticket.html', form=form)


@app.route('/retrieve_ticket', methods=['GET'])
def view_tickets():
    db, cursor = db_connector()
    tickets = []
    try:
        # cursor = get_cursor(db)
        cursor.execute('SELECT id, username, email, date, time, issue, topic FROM tickets')
        tickets = cursor.fetchall()
        print(tickets)  # Debugging line
    finally:
        db.close()

    return render_template('customer_support/retrieve_ticket.html', tickets=tickets)



@app.route('/cust_update_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def cust_update_ticket(ticket_id):
    db = db_connector()
    ticket = None
    try:
        # cursor = get_cursor(db)
        cursor.execute('SELECT username, email, date, time, issue, topic FROM tickets WHERE id = %s', (ticket_id,))
        ticket = cursor.fetchone()

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            date = request.form['date']
            time = request.form['time']
            issue = request.form['issue']
            topic = request.form['topic']

            cursor.execute(
                'UPDATE tickets SET username = %s, email = %s, date = %s, time = %s, issue = %s, topic = %s WHERE id = %s',
                (username, email, date, time, issue, topic, ticket_id)
            )
            db.commit()
            return redirect(url_for('view_tickets'))
    finally:
        cursor.close()
        db.close()

    form = TicketForm(request.form)
    form.username.data = ticket['username']
    form.email.data = ticket['email']
    form.date.data = ticket['date']
    form.time.data = ticket['time']
    form.issue.data = ticket['issue']
    form.topic.data = ticket['topic']

    return render_template('customer_support/update_ticket.html', form=form, ticket_id=ticket_id)


@app.route('/delete_ticket', methods=['POST'])
def delete_ticket():
    ticket_id = request.form['ticket_id']

    db = db_connector()
    try:
        # cursor = get_cursor(db)
        cursor.execute('DELETE FROM tickets WHERE id = %s', (ticket_id,))
        db.commit()
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('view_tickets'))

@app.route('/staff_assignees')
def staff_assignees():
    db , cursor = db_connector()
    try:
        cursor.execute("SELECT id, name, email, role, tickets_solved FROM staff")
        assignees = cursor.fetchall()
        # Sanitize email for safe HTML IDs
        for assignee in assignees:
            assignee['email_id'] = sanitize_email(assignee['email'])
    finally:
        db.close()
    return render_template('customer_support/add_assignees.html', assignees=assignees)


@app.route('/edit_assignee/<string:email>', methods=['GET', 'POST'])
def edit_assignee(email):
    db = db_connector()
    if request.method == 'POST':
        name = request.form.get('name')
        new_email = request.form.get('email')
        role = request.form.get('role')
        tickets_solved = request.form.get('tickets_solved')
        try:
            with db.cursor() as cursor:
                sql = """UPDATE staff
                         SET name = %s, email = %s, role = %s, tickets_solved = %s
                         WHERE email = %s"""
                cursor.execute(sql, (name, new_email, role, tickets_solved, email))
                db.commit()
        except Exception as e:
            db.rollback()
            print("Error:", e)
        finally:
            db.close()
        return redirect(url_for('staff_assignees'))

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM staff WHERE email = %s", (email,))
            assignee = cursor.fetchone()
    finally:
        db.close()
    return render_template('customer_support/edit_assignees.html', assignee=assignee)

@app.route('/add_assignee', methods=['GET', 'POST'])
def add_assignee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        tickets_solved = request.form['tickets_solved']

        db = db_connector()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO staff (name, email, role, tickets_solved) VALUES (%s, %s, %s, %s)',
                    (name, email, role, tickets_solved)
                )
                db.commit()
        except Exception as e:
            db.rollback()
            print("Error:", e)
        finally:
            db.close()

        return redirect(url_for('staff_assignees'))

    return render_template('customer_support/add_assignees.html')

@app.route('/delete_assignee/<string:email>', methods=['POST'])
def delete_assignee(email):
    db = db_connector()
    try:
        with db.cursor() as cursor:
            sql = "DELETE FROM staff WHERE email = %s"
            cursor.execute(sql, (email,))
            db.commit()
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()
    return redirect(url_for('index'))

@app.route('/staff_mytickets')
def staff_mytickets():
    db, cursor = db_connector()
    try:
        with cursor:
            query = """
            SELECT ticketid, username, description, status, priority, created_at, updated_at
            FROM SupportTickets
            WHERE status != 'In Progress'
            """
            cursor.execute(query)
            tickets = cursor.fetchall()
    finally:
        db.close()
    return render_template('customer_support/staff_mytickets.html', tickets=tickets)


@app.route('/staff_update_ticket/<string:ticketid>', methods=['POST'])
def staff_update_ticket(ticketid):
    description = request.form.get('description')
    priority = request.form.get('priority')
    status = request.form.get('status')

    db = db_connector()
    try:
        with db.cursor() as cursor:
            # Modify SQL query to handle string `ticketid`
            sql = """UPDATE SupportTickets
                     SET description = %s, priority = %s, status = %s, updated_at = NOW()
                     WHERE ticketid = %s"""
            cursor.execute(sql, (description, priority, status, ticketid))
            db.commit()
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()
    return redirect(url_for('staff_mytickets'))



@app.route('/thank_you')
def thank_you():
    return render_template('customer_support/thankyou_page.html')




#Insert Report Generaation here
@app.route('/nutrition')
def view_nutrition():
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()
    nutrition_objects = [custnutrition(**entry) for entry in result]
    return render_template('report_generation/nutritionsummary.html', count=len(nutrition_objects), customers=nutrition_objects)


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
    output = io.BytesIO()

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
    return redirect(url_for('staff_view_reports'))


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

    return send_file(pdf_output, as_attachment=True, mimetype='application/pdf', download_name=filename)


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
