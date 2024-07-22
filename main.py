from flask import Flask , render_template, request, redirect, url_for
from db import db_connector
from report_generation.nutritional_summary import custnutrition

app = Flask(__name__)

db, cursor = db_connector()

@app.route('/home')
def home(): 
    return render_template('custhome.html')

@app.route('/customer')
def customer_login(): 
    return render_template('customer.html')

@app.route('/staff')
def staff_login():
    return render_template('/staff.html')

@app.route('/')
def view_nutrition(): 
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()

    nutrition_objects = [custnutrition(**entry) for entry in result]

    
    return render_template('nutritionsummary.html', count=len(nutrition_objects), customers = nutrition_objects)

@app.route('/month-nutrition')
def monthly_nutrition(): 
    cursor.execute("")
    return render_template('monthly-nutritional.html')

#@app.route('/download-csv', methods=['GET'])
#def download_csv(): 
    

if __name__ == '__main__': 
    app.run() 
