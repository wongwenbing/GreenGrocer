import pymysql
import sys
sys.path.append('../GreenGrocer')
from db import db_connector

db, cursor = db_connector()

class NutritionData:
    def __init__(self, nut_id, cust_id, month, total_calories, protein, carbs, vitamins):
        self.nut_id = nut_id
        self.cust_id = cust_id
        self.month = month
        self.total_calories = total_calories
        self.protein = protein
        self.carbs = carbs
        self.vitamins = vitamins
    def __repr__(self):
        return (f'NutritionData(nut_id={self.nut_id}, cust_id={self.cust_id}, month={self.month}, '
                f'total_calories={self.total_calories}, protein={self.protein}, carbs={self.carbs}, '
                f'vitamins={self.vitamins})')

# Fetch data from database
cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
result = cursor.fetchall()
print(result)
# Convert the result to dictionaries
nutrition_objects = [NutritionData(**entry) for entry in result]

# Display the objects
for obj in nutrition_objects:
    print(obj)