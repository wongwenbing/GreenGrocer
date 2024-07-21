import pymysql
import sys
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

class custnutrition:
    def __init__(self, nut_id, cust_id, month, total_calories, protein, carbs, vitamins):
        self.nut_id = nut_id
        self.cust_id = cust_id
        self.month = month
        self.total_calories = total_calories
        self.protein = protein
        self.carbs = carbs
        self.vitamins = vitamins

    def __repr__(self):
        return (f"custnutrition(nut_id={self.nut_id}, cust_id={self.cust_id}, month={self.month}, "
                f"total_calories={self.total_calories}, protein={self.protein}, carbs={self.carbs}, "
                f"vitamins={self.vitamins})")

# Fetch data from database
cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
result = cursor.fetchall()

# Convert the result to dictionaries
data = []
for row in result:
    record = {
        'nut_id': row[0],
        'cust_id': row[1],
        'month': row[2],
        'total_calories': row[3],
        'protein': row[4],
        'carbs': row[5],
        'vitamins': row[6]
    }
    data.append(record)

# Convert dictionaries to custnutrition objects
nutrition_records = [custnutrition(**record) for record in data]

# Display the list of custnutrition objects
for record in nutrition_records:
    print(record)

# Close the database connection
cursor.close()
db.close()
