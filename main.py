from flask import Flask , render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

#@app.route('/') 
#def home() :
 #   return "Hello World"

@app.route('/')
def home(): 
    return render_template('custhome.html')

if __name__ == '__main__': 
    app.run() 

mydb=mysql.connector.connect(
    host="mysql-1698fa8f-wongwenbing0718-aaf0.e.aivencloud.com",
    user="avnadmin",
    password= "AVNS_iBl4eOysp6UaiypUdJd",
    database="greengrocerdb"
)
print(mydb)

cursor = mydb.cursor()

cursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")