from flask import Flask , render_template, request, redirect, url_for
from db import db_connector
from report_generation.nutritional_summary import custnutrition

app = Flask(__name__)


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
    db, cursor = db_connector()
    customer = []   
    cursor.execute("SElECT * FROM Customer_Nutrition")
    result = cursor.fetchall()
    print("Results: ")
    for x in result: 
        customer.append(x)
    
    return render_template('nutritionsummary.html', count=len(customer), customers = customer, x=x)



if __name__ == '__main__': 
    app.run() 
