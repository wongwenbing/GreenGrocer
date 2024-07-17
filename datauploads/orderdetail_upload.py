import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

sql = """
INSERT INTO OrderDetails(order_detail_id, order_id, product_id, quantity)
VALUES (%s, %s, %s, %s);
"""
df = pd.read_csv('orderdetails.csv')
df = df.astype(str)
print(df.dtypes)
list = []
for i, row in df.iterrows(): 
    x = tuple(row)
    list.append(x)

cursor.executemany(sql,list)
db.commit()

cursor.execute("SElECT * FROM OrderDetails")
result = cursor.fetchall()
print("Results: ")
for x in result: 
  print(x)

