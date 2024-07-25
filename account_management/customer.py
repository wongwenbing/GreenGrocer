import sys
sys.path.append('../GreenGrocer')
from db import db_connector


db, cursor = db_connector()
cursor.execute("SELECT * FROM Customers")
result = cursor.fetchall()
print(result)