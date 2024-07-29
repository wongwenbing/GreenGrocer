import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

sql = """
INSERT INTO Products (product_ID, category_id, supplier_id, name, uom, usual_price, country_of_origin, eco_info, ingredients, tags, discount_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
df = pd.read_csv('products table - Sheet1.csv')
df = df.astype(str)
print(df)
list = []
for i, row in df.iterrows():
    x = tuple(row)
    list.append(x)

cursor.executemany(sql,list)
db.commit()

cursor.execute("SElECT * FROM Products")
result = cursor.fetchall()
print("Results: ")
for x in result:
  print(x)

