from flask import Flask , render_template, request, redirect, url_for
from db import db_connector
from report_generation.nutritional_summary import custnutrition
from report_generation.graphs import generate_pie_chart

app = Flask(__name__)

db,cursor = db_connector()

@app.route('/home')
def home(): 
    return render_template('custhome.html')

@app.route('/customer')
def customer_login(): 
    return render_template('customer.html')

@app.route('/staff')
def staff_login():
    return render_template('/staff.html')

@app.route('/nutritionn')
def view_nutrition(): 
    # Fetch data from database
    cursor.execute("SELECT nut_id, cust_id, month, total_calories, protein, carbs, vitamins FROM Customer_Nutrition")
    result = cursor.fetchall()

    nutrition_objects = [custnutrition(**entry) for entry in result]

    
    return render_template('nutritionsummary.html', count=len(nutrition_objects), customers = nutrition_objects)

@app.route('/')
def reports(): 
    graph_json = generate_pie_chart(cursor)

    return render_template('graphs.html', graph_json=graph_json)

if __name__ == '__main__': 
    app.run() 
