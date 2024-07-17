import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

#create table 
""" cursor.execute("""
""" CREATE TABLE StockStatus(
    stock_status_id VARCHAR(45) NOT NULL PRIMARY KEY, 
    stock_status  VARCHAR(200) NOT NULL
) """
""")
db.commit()
 """
 #insert statements
sql = """
INSERT INTO StockStatus(stock_status_id, stock_status)
VALUES (%s, %s);
 """
df = pd.read_csv('stockstatus.csv')
df = df.astype(str)
print(df.dtypes)
list = []
for i, row in df.iterrows(): 
    x = tuple(row)
    list.append(x)

cursor.executemany(sql,list)
db.commit()

cursor.execute("SElECT * FROM StockStatus")
result = cursor.fetchall()
print("Results: ")
for x in result: 
  print(x)

