import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

query = """
INSERT INTO Customers (customer_id, first_name, last_name, email, phone_number, address, block, postal_code, date_of_birth, points, preferred_contact_method)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

df = pd.read_csv('customers.csv')
df = df.astype(str)
print(df.dtypes)
list = []
for i, row in df.iterrows(): 
    x = tuple(row)
    list.append(x)

cursor.executemany(query,list)
db.commit()


print(cursor.rowcount,"record inserted.")

cursor.execute("SELECT * FROM Customers")
result = cursor.fetchall()
print("Results: ")
for x in result: 
  print(x)

