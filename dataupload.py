import pandas as pd
from db import db_connector

db, cursor = db_connector()

def dataupload(sql, df, cursor, db):
    list = []
    for i, row in df.iterrows():
        x = tuple(row)
        list.append(x)

    cursor.executemany(sql, list)
    db.commit()

#sample examples
sql = """
INSERT INTO Categories (category_id, category_name)
VALUES (%s, %s);
"""
df = pd.read_csv('category.csv')
df = df.astype(str)
print(df.dtypes)
list = []
for i, row in df.iterrows():
    x = tuple(row)
    list.append(x)

cursor.executemany(sql,list)
db.commit()

cursor.execute("SElECT * FROM Categories")
result = cursor.fetchall()
print("Results: ")
for x in result:
  print(x)
