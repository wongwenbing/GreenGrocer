from flask import Flask, request, render_template, redirect, url_for
import pymysql
from faqclass import FAQ
from forms import TicketForm


app = Flask(__name__)

def db_connector():
    db = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
        db="greengrocerdb",
        host="mysql-1698fa8f-wongwenbing0718-aaf0.e.aivencloud.com",
        password="AVNS_iBl4eOysp6UaiypUdJd",
        read_timeout=10,
        port=19222,
        user="avnadmin",
        write_timeout=10,
    )
    return db

def get_cursor(db):
    return db.cursor()

# @app.route('/navbar')
# def home():
#     return render_template('navbar.html')

@app.route('/pages-contact')
def contact_us():
    return render_template('pages-contact.html')


@app.route('/pages-faq')
def faq():
    faq_objects = []
    connection = None
    try:
        connection = db_connector()
        if connection is None:
            raise Exception("Failed to establish a database connection.")
        
        with get_cursor(connection) as cursor:
            cursor.execute("SELECT question, answer FROM FAQs LIMIT 10")
            faqs = cursor.fetchall()
            if not faqs:
                print("No FAQs found in the database.")
            for faq in faqs:
                faq_obj = FAQ(faq['question'], faq['answer'])
                faq_objects.append(faq_obj)
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if connection:
            connection.close()

    return render_template('pages-faq.html', faqs=faq_objects)



@app.route('/create_ticket', methods=['GET', 'POST'])
def raise_a_ticket():
    form = TicketForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']
        issue = request.form['issue']
        topic = request.form['topic']

        db = db_connector()
        try:
            cursor = get_cursor(db)
            cursor.execute(
                'INSERT INTO tickets (username, email, date, time, issue, topic) VALUES (%s, %s, %s, %s, %s, %s)',
                (username, email, date, time, issue, topic)
            )
            db.commit()
        finally:
            cursor.close()
            db.close()

        return render_template('thankyou_page.html')

    return render_template('create_ticket.html', form=form)


@app.route('/', methods=['GET'])
def view_tickets():
    db = db_connector()
    tickets = []
    try:
        cursor = get_cursor(db)
        cursor.execute('SELECT id, username, email, date, time, issue, topic FROM tickets')
        tickets = cursor.fetchall()
        print(tickets)  # Debugging line
    finally:
        cursor.close()
        db.close()

    return render_template('retrieve_ticket.html', tickets=tickets)



@app.route('/update_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def update_ticket(ticket_id):
    db = db_connector()
    ticket = None
    try:
        cursor = get_cursor(db)
        cursor.execute('SELECT id, username, email, date, time, issue, topic FROM tickets WHERE id = %s', (ticket_id,))
        ticket = cursor.fetchone()

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            date = request.form['date']
            time = request.form['time']
            issue = request.form['issue']
            topic = request.form['topic']

            cursor.execute(
                'UPDATE tickets SET username = %s, email = %s, date = %s, time = %s, issue = %s, topic = %s WHERE id = %s',
                (username, email, date, time, issue, topic, ticket_id)
            )
            db.commit()
            return redirect(url_for('view_tickets'))
    finally:
        cursor.close()
        db.close()

    form = TicketForm(request.form)
    if ticket:
        form.username.data = ticket['username']
        form.email.data = ticket['email']
        form.date.data = ticket['date']
        form.time.data = ticket['time']
        form.issue.data = ticket['issue']
        form.topic.data = ticket['topic']
    
    return render_template('update_ticket.html', form=form, ticket_id=ticket_id)



@app.route('/delete_ticket', methods=['POST'])
def delete_ticket():
    ticket_id = request.form['ticket_id']

    db = db_connector()
    try:
        cursor = get_cursor(db)
        cursor.execute('DELETE FROM tickets WHERE id = %s', (ticket_id,))
        db.commit()
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('view_tickets'))


@app.route('/thank_you')
def thank_you():
    return 'Thank you for your feedback!'

if __name__ == '__main__':
    app.run(debug=True)
