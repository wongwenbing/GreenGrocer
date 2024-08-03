import pandas as pd
import json
import sys
#set system paath
sys.path.append('../GreenGrocer')
from db import db_connector
db, cursor = db_connector()

class SalesReport:

    def get_ordercount(self):
        query = """
        SELECT COUNT(order_id) AS orderCount FROM Orders;
        """
        cursor.execute(query)
        rows = cursor.fetchone()
        print(rows)
        ordercount = rows['orderCount']
        print(ordercount)