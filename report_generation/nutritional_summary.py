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
    def get_month(self):
        return self.month
    def get_calories(self): 
        return self.total_calories
    def get_protein(self):
        return self.protein
    def get_carbs(self): 
        return self.carbs
    def get_vitamins(self): 
        return self.vitamins
    

# # Fetch data from database
# cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
# result = cursor.fetchall()
#
# nutrition_objects = [custnutrition(**entry) for entry in result]
#
# # Display the objects
# for obj in nutrition_objects:
#     print(obj)