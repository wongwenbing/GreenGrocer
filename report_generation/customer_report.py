import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector
import json
import plotly.express as px
import pandas as pd
import plotly.io as pio

db, cursor = db_connector()
class PurchasingReport:
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


class SustainabilityReport:

    def __init__(self, custid, startdate, enddate):
        self.custid = custid
        self.startdate = startdate
        self.enddate = enddate
        self.emissions_saved = ""
        self.organic_chart = ""
        self.carbon_line = ""
    def carbon_emissions(self):
        query = """
        SELECT SUM(od.quantity*s.carbon_emissions_saved) AS carbon_emissions_saved
        FROM OrderDetails od
        INNER JOIN Products p ON od.product_id = p.product_id
        INNER JOIN Sustainability s ON p.sustainability_id = s.id
        INNER JOIN Orders o ON od.order_id = o.order_id
        WHERE o.datetime BETWEEN %s and %s AND o.customer_id = %s
        """
        cust_id = '1'
        string = ('2023-01-01', '2023-12-31', cust_id)
        cursor.execute(query, string)
        result = cursor.fetchall()
        self.emissions_saved = int(result[0]['carbon_emissions_saved'])

    def graph_organic(self):
        query = """
        SELECT od.quantity, s.organic
        FROM OrderDetails od
        INNER JOIN Products p ON od.product_id = p.product_id
        INNER JOIN Sustainability s ON p.sustainability_id = s.id
        INNER JOIN Orders o ON od.order_id = o.order_id
        WHERE o.datetime BETWEEN %s and %s AND o.customer_id = %s
        """
        cust_id = '1'
        string = ('2023-01-01', '2023-12-31', cust_id)
        cursor.execute(query, string)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        df = df.groupby('organic', as_index=False)['quantity'].sum()
        df = df.sort_values(by=['quantity'], ascending=False)
        df = df.reset_index(drop=True)
        fig = px.pie(df, values='quantity', names='organic', title='Organic or Not?')
        self.organic_chart = pio.to_html(fig, full_html=False)

    def line_carbonemissions(self):
        query = """
        SELECT od.quantity*s.carbon_emissions_saved AS carbon_emissions_saved, MONTHNAME(o.datetime) AS Month, YEAR(o.datetime) AS Year
        FROM OrderDetails od
        INNER JOIN Products p ON od.product_id = p.product_id
        INNER JOIN Sustainability s ON p.sustainability_id = s.id
        INNER JOIN Orders o ON od.order_id = o.order_id
        WHERE o.datetime BETWEEN %s and %s AND o.customer_id = %s
        """
        cust_id = '1'
        string = ('2023-01-01', '2024-08-31', cust_id)
        cursor.execute(query, string)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        df['Month'] = pd.Categorical(df['Month'], categories=calendar.month_name[1:], ordered=True)
        df = df.sort_values('Month')
        df["Month"] = df["Month"].astype(str)
        df["Year"] = df["Year"].astype(str)
        df.rename(columns={'carbon_emissions_saved': 'Carbon Emissions Saved'}, inplace=True)

        df['Combined'] = df[['Year', 'Month']].agg(' '.join, axis=1)
        df = df.sort_values('Combined')
        df['Month Year'] = pd.to_datetime(df['Combined'], format='%Y %B')

        # Sort the DataFrame by the 'Combined' column
        df_sorted = df.sort_values(by='Month Year')
        df = df_sorted.groupby('Month Year', as_index=False)['Carbon Emissions Saved'].sum()

        fig = px.line(df, x='Month Year', y='Carbon Emissions Saved', title='Sales in 2023').update_traces(
            marker=dict(color='green'))
        self.carbon_line = pio.to_html(fig, full_html=False)


# report = PurchasingReport('2023-08-14', '2024-08-06', 'Purchasing Report')
# report.get_average_order_spending()
# report.get_total_amount()
# report.get_mostpurchased_category()
# print(report.average)

# class SustainabilityReport (self):
#     def get_total_in_a_year(self):