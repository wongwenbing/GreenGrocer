import pymysql 
from db import establish_connection

class User_Item(): 
    def __init(self, userid, purchase_date, item, category, qty, protein, carbs, fibre, keynutrients):
        self.__userid = userid
        self.__purchase_date = purchase_date
        self.__item = item 
        self.__category = category
        self.__qty = qty
        self.__protein = protein
        self.__carbs = carbs
        self.__fibre = fibre
        self.__keynutrients = keynutrients
        
    def get_user_id(s): 
        self.