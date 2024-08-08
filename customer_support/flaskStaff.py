from flask import Flask, request, render_template, redirect, url_for
import pymysql
from datetime import datetime
import re

app = Flask(__name__)

def sanitize_email(email):
    return re.sub(r'[^\w]', '_', email)

# Database connector function
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

# Combine with the rest
# @app.route('/')
# def home():
#     return render_template('navbar.html')

@app.route('/staff_assignees')
def index():
    db = db_connector()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id, name, email, role, tickets_solved FROM staff")
            assignees = cursor.fetchall()
            # Sanitize email for safe HTML IDs
            for assignee in assignees:
                assignee['email_id'] = sanitize_email(assignee['email'])
    finally:
        db.close()
    return render_template('staff_assignees.html', assignees=assignees)


@app.route('/edit_assignee/<string:email>', methods=['GET', 'POST'])
def edit_assignee(email):
    db = db_connector()
    if request.method == 'POST':
        name = request.form.get('name')
        new_email = request.form.get('email')
        role = request.form.get('role')
        tickets_solved = request.form.get('tickets_solved')
        try:
            with db.cursor() as cursor:
                sql = """UPDATE staff
                         SET name = %s, email = %s, role = %s, tickets_solved = %s
                         WHERE email = %s"""
                cursor.execute(sql, (name, new_email, role, tickets_solved, email))
                db.commit()
        except Exception as e:
            db.rollback()
            print("Error:", e)
        finally:
            db.close()
        return redirect(url_for('index'))

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM staff WHERE email = %s", (email,))
            assignee = cursor.fetchone()
    finally:
        db.close()
    return render_template('edit_assignees.html', assignee=assignee)

@app.route('/add_assignee', methods=['GET', 'POST'])
def add_assignee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        tickets_solved = request.form['tickets_solved']

        db = db_connector()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO staff (name, email, role, tickets_solved) VALUES (%s, %s, %s, %s)',
                    (name, email, role, tickets_solved)
                )
                db.commit()
        except Exception as e:
            db.rollback()
            print("Error:", e)
        finally:
            db.close()

        return redirect(url_for('index'))

    return render_template('add_assignees.html')

@app.route('/delete_assignee/<string:email>', methods=['POST'])
def delete_assignee(email):
    db = db_connector()
    try:
        with db.cursor() as cursor:
            sql = "DELETE FROM staff WHERE email = %s"
            cursor.execute(sql, (email,))
            db.commit()
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()
    return redirect(url_for('index'))

@app.route('/staff_mytickets')
def tickets():
    db = db_connector()
    try:
        with db.cursor() as cursor:
            query = """
            SELECT ticketid, username, description, status, priority, created_at, updated_at
            FROM SupportTickets
            """
            cursor.execute(query)
            tickets = cursor.fetchall()

            # Format the datetime fields
            for ticket in tickets:
                ticket['created_at'] = ticket['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                ticket['updated_at'] = ticket['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
    finally:
        db.close()
    return render_template('staff_mytickets.html', tickets=tickets)



@app.route('/update_ticket/<string:ticketid>', methods=['POST'])
def update_ticket(ticketid):
    description = request.form.get('description')
    priority = request.form.get('priority')
    status = request.form.get('status')
    created_at = request.form.get('created_at')
    updated_at = request.form.get('updated_at')

    # Convert the datetime-local format back to the original format used in the database
    created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    updated_at = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

    db = db_connector()
    try:
        with db.cursor() as cursor:
            sql = """UPDATE SupportTickets
                     SET description = %s, priority = %s, status = %s, created_at = %s, updated_at = %s
                     WHERE ticketid = %s"""
            cursor.execute(sql, (description, priority, status, created_at, updated_at, ticketid))
            db.commit()
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()
    return redirect(url_for('tickets'))



if __name__ == '__main__':
    app.run(debug=True)
