import sys
#set system paath
sys.path.append('../GreenGrocer')
from db import db_connector
db, cursor = db_connector()
import plotly.express as px
import pandas as pd
import plotly.io as pio


class SalesReport:
    def __init__(self, startdate, enddate):
        self.startdate = startdate
        self.enddate = enddate
        self.totalorders = ""
        self.chart = ""
        self.average = ""

    def get_info(self):
        return f"start: {self.startdate}, end: {self.enddate}"

    def get_total_amount(self):
        query = """
        SELECT COUNT(order_id) AS orderCount FROM Orders
        WHERE Orders.datetime BETWEEN %s AND %s
                """
        string = (self.startdate, self.enddate)
        cursor.execute(query, string)
        rows = cursor.fetchall()
        print(rows)
        ordercount = rows[0]
        ordercount = ordercount['orderCount']
        self.totalorders = ordercount

    def get_average_order_spending(self):
        query = """
        SELECT o.order_id, o.quantity*p.usual_price AS sales
        FROM OrderDetails o 
        INNER JOIN Products p ON o.product_id = p.product_id
        INNER JOIN Orders od ON od.order_id = o.order_id
        WHERE od.datetime BETWEEN %s AND %s
        """
        string = (self.startdate, self.enddate)
        cursor.execute(query, string)
        result = cursor.fetchall()
        print(result)
        result = pd.DataFrame(result)
        df = result.groupby('order_id', as_index=False)['sales'].sum()
        print(df)
        df = df['sales']
        df = df.mean()
        self.average = f"{df:.2f}"

    def get_mostpurchased_category(self):
        query = """
                SELECT od.quantity, p.name, c.category_name
                FROM OrderDetails od
                INNER JOIN Products p ON od.product_id = p.product_id
                INNER JOIN Categories c ON p.category_id = c.category_id
                INNER JOIN Orders o ON od.order_id = o.order_id
                WHERE o.datetime BETWEEN %s AND %s
        """
        string = (self.startdate, self.enddate)
        cursor.execute(query, string)
        rows = cursor.fetchall()
        print(rows)
        df = pd.DataFrame(rows)
        df = df.groupby('category_name', as_index=False)['quantity'].sum()
        df = df.sort_values(by=['quantity'], ascending=False)
        df = df.reset_index(drop=True)
        print(df)
        fig = px.bar(df, x='category_name', y='quantity').update_traces(marker=dict(color='green'))
        self.chart = pio.to_html(fig, full_html=False)

class InventoryReport:
    def __init__(self):
        self.total_inventory_value = 0
        self.chart = 0
        self.avg_stock = 0

    def get_totalinventory(self):
        # total inventory value
        query = """
        SELECT SUM(i.stock_quantity*p.usual_price) AS Total_Inventory_Value
        FROM Inventory i
        INNER JOIN Products p
        ON i.product_id = p.product_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.total_inventory_value = rows[0]['Total_Inventory_Value']

    def get_totalinventoryvalue_bycategory(self):
        # total inventory value by product category distribution
        query = """
        SELECT i.stock_quantity*p.usual_price AS total_inventory_value , p.category_id, c.category_name
        FROM Inventory i
        INNER JOIN Products p
        ON i.product_id = p.product_id
        INNER JOIN Categories c
        ON p.category_id = c.category_id
        """
        cursor.execute(query)
        rows = pd.DataFrame(cursor.fetchall())
        df = rows.groupby('category_name', as_index=False)['total_inventory_value'].sum()
        df = df.sort_values(by=['total_inventory_value'], ascending=False)
        df.rename(columns={'total_inventory_value': 'Total Inventory Value', 'category_name': 'Category'}, inplace=True)

        df = df.reset_index(drop=True)
        fig = px.bar(df, x='Category', y='Total Inventory Value',
                     title='Total Inventory Value by Product Category').update_traces(marker=dict(color='green'))
        self.chart = pio.to_html(fig, full_html=False)

    def get_average_stock(self):
        query = "SELECT AVG(stock_quantity) FROM Inventory"
        cursor.execute(query)
        rows = cursor.fetchall()
        self.avg_stock = f"{rows[0]['AVG(stock_quantity)']:.2f}"

class CategoryReport:

    def __init__(self):
        self.category = ""

#
# query = """
#         SELECT od.quantity, p.name, c.category_name
#         FROM Ord        INNER JOIN Products p ON od.product_id = p.product_id
#         INNER JOIN Categories c ON p.category_id = c.category_id
#         INNER JOIN Orders o ON od.order_id = o.order_id
#         WHERE o.datetime BETWEEN %s AND %s
# """
# cursor.execute(query,string)
# rows = cursor.fetchall()
# df = pd.DataFrame(rows)
# df = df.groupby('category_name', as_index=False)['quantity'].sum()
# df = df.sort_values(by=['quantity'], ascending=False)
# df1 = df.reset_index(drop=True)
#
# query = """
#         SELECT od.quantity, p.name, c.category_name
#         FROM OrderDetails od
#         INNER JOIN Products p ON od.product_id = p.product_id
#         INNER JOIN Orders o ON od.order_id = o.order_id
#         WHERE o.datetime BETWEEN %s AND %s
# """
# cursor.execute(query,string)
# rows = cursor.fetchall()
# df = pd.DataFrame(rows)
# df = df.groupby('category_name', as_index=False)['quantity'].sum()
# df = df.sort_values(by=['quantity'], ascending=False)
# df2 = df.reset_index(drop=True)
#
#
# query = """
# SELECT o.order_id, o.quantity*p.usual_price AS sales
# FROM OrderDetails o
# INNER JOIN Products p ON o.product_id = p.product_id
# INNER JOIN Orders od ON od.order_id = o.order_id
# WHERE od.datetime BETWEEN %s AND %s
# """
# cursor.execute(query, string)
# result = cursor.fetchall()
# result = pd.DataFrame(result)
# df3 = result.groupby('order_id', as_index=False)['sales'].sum()
#
# file_path = 'SalesReport.xlsx'
#
#
# # Write DataFrames to the same Excel file, each to a different sheet
# with pd.ExcelWriter(file_path) as writer:
#     df1.to_excel(writer, sheet_name='Sales by Category', index=False)
#     df2.to_excel(writer, sheet_name='Sales by Product', index=False)
#     df2.to_excel(writer, sheet_name='Sales by Order', index=False)