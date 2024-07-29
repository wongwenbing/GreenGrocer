import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

query = """
UPDATE OrderDetails SET product_id =  %s WHERE order_detail_id = %s
"""

df = pd.read_csv('Sample Data - OrderDetail.csv')
df = df.astype(str)
print(df)
list = []
for i, row in df.iterrows():
    x = tuple(row)
    list.append(x)

cursor.executemany(query, list)
db.commit()


print(cursor.rowcount,"record inserted.")

cursor.execute("SELECT * FROM OrderDetails")
result = cursor.fetchall()
print("Results: ")
for x in result:
  print(x)

