import pandas as pd 
import pymysql
import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()


df = pd.read_csv("report_generation/nut.csv")
df = df.astype(str)
print(df.dtypes)
list = []
for i, row in df.iterrows(): 
    x = tuple(row)
    list.append(x)

sql = """
INSERT INTO Customer_Nutrition(cust_id, month, total_calories, protein, carbs, vitamins)
VALUES (%s, %s, %s, %s, %s, %s);
"""
cursor.executemany(sql,list)
db.commit()

cursor.execute("SElECT * FROM Customer_Nutrition")
result = cursor.fetchall()
print("Results: ")
for x in result: 
  print(x)

