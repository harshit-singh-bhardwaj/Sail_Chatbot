from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pandas as pd
import os
import logging
import bcrypt
import webbrowser
import sqlite3
import secrets
from threading import Timer
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# SQLite Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load the CSV dataset
faq_data = pd.read_csv("data/sail_faq.csv")

# Convert CSV to nested dictionary structure
def build_tree(data):
    tree = {}
    for _, row in data.iterrows():
        current = tree
        for level in ['Level1', 'Level2', 'Level3']:
            key = row[level]
            if pd.isna(key) or key.strip() == "-":
                break
            if key not in current:
                current[key] = {}
            current = current[key]
        current["response"] = row["Response"]
    return tree

faq_tree = build_tree(faq_data)
conversation_state = {}

# Existing routes (Login, Register, etc.)
@app.route('/')
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['email'] = email
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid email or password.")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if email already exists in main users table
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', error="Email already exists.")

        # Store in account_requests table
        cursor.execute("INSERT INTO account_requests (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()

        return render_template('register.html', error="Request submitted. Admin will review your account.")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Chatbot route
@app.route('/chat', methods=['POST'])
def chat():
    if 'email' not in session:
        return jsonify({"response": "Please log in to use the chatbot."})

    user_input = request.json.get("message")
    session_id = request.remote_addr

    if user_input.lower() in ["yes", "start over", "restart"]:
        conversation_state[session_id] = {"tree": faq_tree, "history": []}
        return jsonify({
            "response": "Welcome back to the main menu. Please select an option:",
            "dropdown": list(faq_tree.keys())
        })

    if user_input.lower() in ["no", "exit", "quit"]:
        conversation_state.pop(session_id, None)
        return jsonify({"response": "Thank you for using SAIL Chatbot!"})

    if session_id not in conversation_state:
        conversation_state[session_id] = {"tree": faq_tree, "history": []}
        return jsonify({
            "response": "Hello! Welcome to SAIL. Please select an option:",
            "dropdown": list(faq_tree.keys())
        })

    state = conversation_state[session_id]
    current_tree = state["tree"]

    if user_input in current_tree:
        next_branch = current_tree[user_input]
        state["history"].append(user_input)
        if "response" in next_branch:
            conversation_state[session_id]["tree"] = {}
            return jsonify({
                "responses": [
                    next_branch["response"],
                    "Do you want to go back to the main menu?"
                ],
                "dropdown": ["Yes", "No"]
            })
        else:
            state["tree"] = next_branch
            return jsonify({
                "response": f"You selected '{user_input}'. Please choose one of the following:",
                "dropdown": list(next_branch.keys())
            })
    else:
        return jsonify({
            "response": "Sorry, I didn't understand that. Please select from the given options.",
            "dropdown": list(current_tree.keys())
        })

# Forgot Password Route
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if user:
            # ✅ Generate secure token
            token = secrets.token_urlsafe(32)
            expiry = datetime.utcnow() + timedelta(hours=1)

            # ✅ Insert into table with token and expiry
            cursor.execute('''
                INSERT INTO password_requests (email, token, expiry, status)
                VALUES (?, ?, ?, ?)
            ''', (email, token, expiry, 'Pending'))

            conn.commit()
            conn.close()

            # You can redirect with success message
            return redirect(url_for('forgot_password', success="Password reset request sent."))
        else:
            error = "Email not registered."
            conn.close()

    return render_template('forgot_password.html', error=error)

# Admin login route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'Admin@sail.com' and password == '123':
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

# Admin dashboard route
@app.route('/admin-dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch Users
    cursor.execute("SELECT id, email, password FROM users")
    users = cursor.fetchall()

    # Fetch Account Requests
    cursor.execute("SELECT id, email, password, created_at FROM account_requests")
    account_requests = cursor.fetchall()

    # Fetch Password Reset Requests by Status
    cursor.execute("SELECT id, email, request_time, status FROM password_requests WHERE status = 'Pending' ORDER BY request_time DESC")
    pending_password_requests = cursor.fetchall()

    cursor.execute("SELECT id, email, request_time, status FROM password_requests WHERE status = 'Completed' ORDER BY request_time DESC")
    approved_password_requests = cursor.fetchall()

    cursor.execute("SELECT id, email, request_time, status FROM password_requests WHERE status = 'Rejected' ORDER BY request_time DESC")
    rejected_password_requests = cursor.fetchall()

    conn.close()
    return render_template(
        'admin_dashboard.html',
        users=users,
        account_requests=account_requests,
        pending_password_requests=pending_password_requests,
        approved_password_requests=approved_password_requests,
        rejected_password_requests=rejected_password_requests
    )

# Delete user route
@app.route('/admin/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Edit user route
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if request.method == 'POST':
        new_email = request.form['email']
        conn.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/account-requests')
def account_requests():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM account_requests')
    requests = [dict(id=row[0], email=row[1], password=row[2], created_at=row[3]) for row in cursor.fetchall()]
    conn.close()
    return render_template('account_requests.html', requests=requests)

@app.route('/admin/approve_account/<int:request_id>', methods=['GET', 'POST'])
def approve_account(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, password FROM account_requests WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()

    if request_data:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (request_data['email'], request_data['password']))
        cursor.execute("DELETE FROM account_requests WHERE id = ?", (request_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/deny_account/<int:request_id>', methods=['GET', 'POST'])
def deny_account(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM account_requests WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Admin reset password from admin dashboard route
@app.route('/admin/reset-password/<int:request_id>', methods=['POST'])
def reset_password_from_admin(request_id):
    new_password = request.form.get("new_password")
    print(f"Request ID: {request_id}, New Password: {new_password}")  # Debug line

    if not new_password:
        return "Missing new password", 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Fetch email from password_requests table
    cursor.execute("SELECT email FROM password_requests WHERE id=?", (request_id,))
    row = cursor.fetchone()

    if row:
        email = row[0]
        cursor.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
        cursor.execute("UPDATE password_requests SET status=? WHERE id=?", ('Completed', request_id))
        conn.commit()

        cursor.execute("SELECT id, email, status FROM password_requests WHERE id=?", (request_id,))
        updated_row = cursor.fetchone()
        print("Password request after update:", updated_row)

    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route('/admin/reject-password-request/<int:request_id>', methods=['POST'])
def reject_password_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE password_requests SET status = 'Rejected' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

def open_browser():
    webbrowser.open("http://0.0.0.0:5001/")

if __name__ == "__main__":
    logging.basicConfig(filename='logs/chatbot.log', level=logging.INFO)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5001, debug=True)