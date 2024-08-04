import pymysql
from db import db_connector
from decimal import Decimal


class DAO:
    def __init__(self):
        self.connection = db_connector()
    
    def __del__(self):
        if self.connection:
            self.connection.close()
    
    # Product Methods
    def get_all_products(self, status_filter=None):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # Base query to fetch products with their category name and discounted price
            query = """
            SELECT p.*, c.category_name,
                IFNULL(d.discount_percentage, 0) AS discount_percentage,
                ROUND(p.usual_price * (1 - IFNULL(d.discount_percentage, 0) / 100), 2) AS discounted_price
            FROM Products p
            JOIN Categories c ON p.category_id = c.category_id
            LEFT JOIN Discounts d ON p.discount_id = d.discount_id
            """
            
            # Apply status filter if provided
            if status_filter:
                query += " WHERE p.status = %s"
                params = (status_filter,)
            else:
                params = ()  # No filter applied
            
            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()
            
    def get_product_by_id(self, product_id):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT p.product_ID, p.category_id, p.supplier_id, p.name, p.uom, p.usual_price, 
                    p.country_of_origin, p.eco_info, p.ingredients, p.tags,
                    p.discount_id,IFNULL(d.discount_percentage, 0) AS discount_percentage,
                    ROUND(p.usual_price * (1 - IFNULL(d.discount_percentage, 0) / 100), 2) AS discounted_price, p.status
            FROM Products p
                LEFT JOIN Discounts d ON p.discount_id = d.discount_id
                WHERE p.product_ID = %s
            """
            cursor.execute(query, (product_id,))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()

    def create_product(self, product_id, category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status):
        cursor = None
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO Products (product_ID, category_id, supplier_id, name, uom, usual_price, 
                country_of_origin, eco_info, ingredients, tags, discount_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (product_id, category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status))
            self.connection.commit()
        finally:
            if cursor:
                cursor.close()
            
    def update_product(self, product_id, category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status):
        cursor = None
        try:
            cursor = self.connection.cursor()

            # Convert price to Decimal for better precision
            if price is not None:
                price = Decimal(price)
            
            # Update the product information
            update_query = """
                UPDATE Products
                SET category_id = %s, supplier_id = %s, name = %s, uom = %s, usual_price = %s,
                    country_of_origin = %s, eco_info = %s, ingredients = %s, tags = %s,
                    discount_id = %s, status = %s
                WHERE product_ID = %s
            """
            params = (category_id, supplier_id, name, uom, price, country_of_origin, eco_info, ingredients, tags, discount_id, status, product_id)
            cursor.execute(update_query, params)
            self.connection.commit()

        except pymysql.MySQLError as e:
            self.connection.rollback()
            print(f"MySQL error occurred: {e}")
            raise
        except Exception as e:
            self.connection.rollback()
            print(f"An error occurred: {e}")
            raise
        finally:
            if cursor:
                cursor.close()



    def delete_product(self, product_id):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM Products WHERE product_ID=%s', (product_id,))
            self.connection.commit()
        finally:
            if cursor:
                cursor.close()

    # Cart Methods
    def get_cart_by_customer_id(self, customer_id):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT c.cart_id, cd.product_id, cd.quantity, p.name, p.usual_price, 
                    IFNULL(d.discount_percentage, 0) AS discount_percentage
                FROM Cart c
                JOIN Cart_Details cd ON c.cart_id = cd.cart_id
                JOIN Products p ON cd.product_id = p.product_ID
                LEFT JOIN Discounts d ON p.discount_id = d.discount_id
                WHERE c.customer_id = %s
            """, (customer_id,))

            cart_items = cursor.fetchall()

            # Calculate discounted price
            for item in cart_items:
                item['discounted_price'] = item['usual_price'] * (1 - (item['discount_percentage'] / 100))

            return cart_items
        finally:
            if cursor:
                cursor.close()


    def add_product_to_cart(self, customer_id, product_id, quantity):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT cart_id FROM Cart WHERE customer_id = %s", (customer_id,))
            cart = cursor.fetchone()
            
            if not cart:
                cursor.execute("INSERT INTO Cart (customer_id, created_at) VALUES (%s, NOW())", (customer_id,))
                self.connection.commit()
                cart_id = cursor.lastrowid
            else:
                cart_id = cart['cart_id']
            
            cursor.execute("""
                INSERT INTO Cart_Details (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """, (cart_id, product_id, quantity))
            self.connection.commit()
        finally:
            if cursor:
                cursor.close()

    def update_cart_item(self, customer_id, product_id, quantity):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT cart_id FROM Cart WHERE customer_id = %s", (customer_id,))
            cart = cursor.fetchone()
            
            if cart:
                cart_id = cart['cart_id']
                cursor.execute("""
                    UPDATE Cart_Details
                    SET quantity = %s
                    WHERE cart_id = %s AND product_id = %s
                """, (quantity, cart_id, product_id))
                self.connection.commit()
        finally:
            if cursor:
                cursor.close()

    def delete_cart_item(self, customer_id, product_id):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT cart_id FROM Cart WHERE customer_id = %s", (customer_id,))
            cart = cursor.fetchone()
            
            if cart:
                cart_id = cart['cart_id']
                cursor.execute("""
                    DELETE FROM Cart_Details
                    WHERE cart_id = %s AND product_id = %s
                """, (cart_id, product_id))
                self.connection.commit()
        finally:
            if cursor:
                cursor.close()

    def clear_cart(self, customer_id):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT cart_id FROM Cart WHERE customer_id = %s", (customer_id,))
            cart = cursor.fetchone()
            
            if cart:
                cart_id = cart['cart_id']
                cursor.execute("""
                    DELETE FROM Cart_Details
                    WHERE cart_id = %s
                """, (cart_id,))
                self.connection.commit()
        finally:
            if cursor:
                cursor.close()

    def get_products_by_category(self, category_id, status_filter='active'):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
                SELECT p.*, c.category_name,
                    IFNULL(d.discount_percentage, 0) AS discount_percentage,
                    ROUND(p.usual_price * (1 - IFNULL(d.discount_percentage, 0) / 100), 2) AS discounted_price
                FROM Products p
                JOIN Categories c ON p.category_id = c.category_id
                LEFT JOIN Discounts d ON p.discount_id = d.discount_id
                WHERE p.category_id = %s AND p.status = %s
            """
            cursor.execute(query, (category_id, status_filter))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()

    def get_all_categories(self):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM Categories")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
    
    def get_products_by_search(self, search_query=None, status_filter='active'):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = """
            SELECT p.*, c.category_name,
                IFNULL(d.discount_percentage, 0) AS discount_percentage,
                ROUND(p.usual_price * (1 - IFNULL(d.discount_percentage, 0) / 100), 2) AS discounted_price
            FROM Products p
            JOIN Categories c ON p.category_id = c.category_id
            LEFT JOIN Discounts d ON p.discount_id = d.discount_id
            WHERE p.name LIKE %s AND p.status = %s
            """
            cursor.execute(query, ('%' + search_query + '%', status_filter))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
    
    def get_all_suppliers(self):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            # Select distinct supplier_name, and fetch their IDs if needed
            query = """
            SELECT supplier_id, supplier_name 
            FROM Suppliers
            WHERE supplier_name IN (
                SELECT DISTINCT supplier_name
                FROM Suppliers
            )
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
                if cursor:
                    cursor.close()
    
    def get_all_discounts_from_products(self, status_filter=None):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            
            # Query to fetch distinct discounts from products
            query = """
            SELECT DISTINCT d.discount_id, d.discount_percentage
            FROM Products p
            LEFT JOIN Discounts d ON p.discount_id = d.discount_id
            """
            
            # Apply status filter if provided
            if status_filter:
                query += " WHERE p.status = %s"
                params = (status_filter,)
            else:
                params = ()  # No filter applied
            
            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

    def get_all_discounts(self):
        cursor = None
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT discount_id, discount_percentage FROM Discounts")
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()


    def update_product_discounted_price(self, product_id, discounted_price):
        query = "UPDATE Products SET discounted_price = %s WHERE product_id = %s"
        params = (discounted_price, product_id)
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
        finally:
            if cursor:
                cursor.close()
