from flask import Flask , render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def home(): 
    return render_template('custhome.html')

@app.route('/customer')
def customer_login(): 
    return render_template('customer.html')

@app.route('/staff')
def staff_login():
    return render_template('/staff.html')

if __name__ == '__main__': 
    app.run() 
