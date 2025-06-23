from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
from datetime import datetime
from num2words import num2words
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
DB_FILE = 'rentbook.db'
conn = sqlite3.connect("rentbook.db", check_same_thread=False)
cursor = conn.cursor()



def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize DB ---
def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            flat_no TEXT UNIQUE,
            rent_per_month REAL,
            dues REAL,
            date_of_occupance TEXT,
            contract_issued_date TEXT,
            tenant_document TEXT
        )''')

@app.before_request
def setup():
    init_db()

@app.route('/styles.css')
def serve_css():
    return send_from_directory('.', 'styles.css')

@app.route('/')
def index():
    with get_db() as conn:
        tenants = conn.execute("SELECT * FROM tenants").fetchall()
    return render_template('index.html', tenants=tenants)

@app.route('/add', methods=['GET', 'POST'])
@app.route('/edit/<int:tenant_id>', methods=['GET', 'POST'])
def add_tenant(tenant_id=None):
    tenant = None
    with get_db() as conn:
        if tenant_id:
            tenant = conn.execute("SELECT * FROM tenants WHERE id=?", (tenant_id,)).fetchone()

    if request.method == 'POST':
        data = (
            request.form['first_name'],
            request.form['last_name'],
            request.form['flat_no'],
            float(request.form['rent_per_month']),
            float(request.form['dues']),
            request.form['date_of_occupance'],
            request.form['contract_issued_date']
        )
        file = request.files.get('tenant_document')
        file_path = None
        if file and file.filename.endswith('.pdf'):
            filename = f"{data[0]}_{data[1]}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        with get_db() as conn:
            if tenant:
                conn.execute('''
                    UPDATE tenants SET
                        first_name=?, last_name=?, flat_no=?, rent_per_month=?, dues=?,
                        date_of_occupance=?, contract_issued_date=?, tenant_document=?
                    WHERE id=?
                ''', (*data, file_path, tenant_id))
            else:
                conn.execute('''
                    INSERT INTO tenants (
                        first_name, last_name, flat_no, rent_per_month, dues,
                        date_of_occupance, contract_issued_date, tenant_document
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (*data, file_path))

        return redirect(url_for('index'))

    return render_template('add_tenant.html', tenant=tenant)

@app.route('/receipt/<int:tenant_id>', methods=['GET', 'POST'])
def generate_receipt(tenant_id):
    current_year = datetime.now().year
    with get_db() as conn:
        tenant = conn.execute("SELECT * FROM tenants WHERE id=?", (tenant_id,)).fetchone()

    if request.method == 'POST':
        amount_paid = float(request.form['amount_paid'])
        receipt_date = request.form['receipt_date']
        month = request.form['month']
        year = request.form['year']

        new_dues = tenant['dues'] - amount_paid
        if new_dues < 0:
            new_dues = 0

        with get_db() as conn:
            conn.execute("UPDATE tenants SET dues=? WHERE id=?", (new_dues, tenant_id))

        amount_in_words = num2words(amount_paid, to='currency', lang='en_IN').replace('euro', 'Rupees').replace('cents', 'paise')

        return render_template(
            'receipt.html',
            tenant=tenant,
            amount_paid=amount_paid,
            receipt_date=receipt_date,
            month=month,
            year=year,
            amount_in_words=amount_in_words
        )

    return render_template('receipt_form.html', tenant=tenant, current_year=current_year)

@app.route('/delete/<int:tenant_id>', methods=['POST'])
def delete_tenant(tenant_id):
    with get_db() as conn:
        conn.execute("DELETE FROM tenants WHERE id=?", (tenant_id,))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='0.0.0.0', port=80)

