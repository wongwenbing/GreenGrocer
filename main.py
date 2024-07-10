from flask import Flask , render_template, request, redirect, url_for

app = Flask(__name__)

#@app.route('/') 
#def home() :
 #   return "Hello World"

@app.route('/')
def home(): 
    return render_template('custhome.html')

if __name__ == '__main__': 
    app.run() 
    