import pymysql 
from db import establish_connection

cursor = establish_connection()

class cust_nut(): 
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
        
    def set_user_id(self, userid): 
        self.__userid = userid
    def set_purchase_date(self, purchase_date):
        self.__purchase_date = purchase_date
    def set_item(self, item): 
        self.__item= item 
    def set_category(self, category): 
        self.__category = category
    def set_qty(self, qty): 
        self.__qty = qty
    def set_protein(self, protein): 
        self.__protein = protein 
    def set_carbs(self, carbs):
        self.__carbs = carbs
    def set_fibre(self, fibre): 
        self.__fibre = fibre
    def set_keynutrients(self, keynutrients): 
        self.__keynutrients = keynutrients
    
    def get_userid(self): 
        return self.__userid
    def get_purchasedate(self): 
        return self.__purchase_date
    def get_item(self): 
        return self.__item
    def get_category(self): 
        return self.__category
    def get_qty(self): 
        return self.__qty
    def get_protein(self): 
        return self.__protein
    def get_carbs(self): 
        return self.__carbs
    def get_fibre(self): 
        return self.__fibre
    def get_keynutrients(self): 
        return self.__keynutrients
        
