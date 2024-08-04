from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import db_connector
import pymysql
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart
from report_generation.invoice import InvoiceCustomer, Items
from report_generation.reportgen import CustReport, customer_report, StaffReport, staff_report
from account_management.forms import CreateUserForm, RegistrationForm
import os
from products.dao import DAO
from db import *
from decimal import Decimal 


app = Flask(__name__)

app.secret_key = os.urandom(24)  # Generates a random secret key each time

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

# Insert Account Generation here

# Login, Sign up, Profile

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db, cursor = db_connector()

        cursor.execute('SELECT * FROM users WHERE email = %s', (email))
        user = cursor.fetchone()

        if not user:
            cursor.execute('SELECT * FROM staff WHERE email = %s', (email))
            user = cursor.fetchone()
            role = 'staff' if user else None
        else:
            role = 'users'

        
        db.close()
        
        if user and user['password'] == password:
            session['id'] = user['id']
            session['role'] = role
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
            db, cursor = db_connector()
            cursor.execute('''
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
    role = session['role']

    db, cursor = db_connector()

    if request.method == 'POST':
        if 'delete_account' in request.form:
            cursor.execute(f'DELETE FROM {role} WHERE id = %s', (id))
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
            query = f"""
UPDATE {role}
SET name = %s, email = %s, phone_number = %s, address = %s, date_of_birth = %s
WHERE id = %s
"""
            cursor.execute(query, val)
            db.commit()
            flash('Profile updated successfully!', 'success')
    
    cursor.execute(f'SELECT * FROM {role} WHERE id = %s', (id))
    user = cursor.fetchone()
    db.close()
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


dao = DAO()
#Insert Transaction Processing here
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

    return render_template('index.html', products=products, categories=categories,
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

    return render_template('product_detail.html', product=product, featured_products=featured_products)

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
    return render_template('cart.html', cart_items=cart_items, customer_id=customer_id)

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

@app.route('/admin/products', methods=['GET'])
def admin_products():
    status_filter = request.args.get('status')  # Get filter from request
    
    if status_filter not in ['active', 'drafts', 'archive', None]:
        status_filter = None  # Default to showing all products if the status filter is invalid

    products = dao.get_all_products(status_filter=status_filter)
    
    # Debug: Print or log the products and status filter
    print(f"Status Filter: {status_filter}")
    print(f"Products: {products}")

    return render_template('admin_products.html', products=products, status_filter=status_filter)


@app.route('/admin/product/<product_id>')
def admin_product_detail(product_id):
    product = dao.get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))
    return render_template('admin_product_detail.html', product=product)

## Admin add product
@app.route('/admin/add_product', methods=['GET', 'POST'])
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

    return render_template('admin_add_product.html', categories=categories, suppliers=suppliers, discounts=discounts)



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

    return render_template('admin_edit_product.html', product=product, categories=categories, suppliers=suppliers, discounts=discounts)


@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def admin_delete_product(product_id):
    dao.delete_product(product_id)
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    app.run(debug=True)


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
