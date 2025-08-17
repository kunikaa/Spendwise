from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
DB_NAME = "expenses.db"

# --- Database Init ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS expenses
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        category TEXT,
                        amount REAL,
                        description TEXT)''')
    conn.close()

init_db()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                    (date, category, amount, description))
        conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        with sqlite3.connect(DB_NAME) as conn:
            df.to_sql('expenses', conn, if_exists='append', index=False)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
    
    # Basic summary
    total = df['amount'].sum() if not df.empty else 0
    by_category = df.groupby('category')['amount'].sum().to_dict() if not df.empty else {}
    
    return render_template('dashboard.html', tables=df.to_dict(orient='records'),
                           total=total, by_category=by_category)

if __name__ == '__main__':
    app.run(debug=True)
