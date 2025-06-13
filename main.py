from flask import *
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

app=Flask(__name__)
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client["RentBook"]
tenants_collection = db["RentBookTenants"]
tenants_collection.create_index("flat_no", unique=True)



@app.route('/styles.css')
def serve_css():
    return send_from_directory('.', 'styles.css')

@app.route('/')
def index():
    tenants = list(tenants_collection.find())
    return render_template('index.html', tenants=tenants)


@app.route('/add', methods=['GET', 'POST'])
@app.route('/edit/<tenant_id>', methods=['GET', 'POST'])
def add_tenant(tenant_id=None):
    tenant = None
    if tenant_id:
        tenant = tenants_collection.find_one({'_id': ObjectId(tenant_id)})
    if request.method == 'POST':
        tenant_data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "no_of_residents": int(request.form['no_of_residents']),
            "dues_remaining": float(request.form['dues_remaining']),
            "flat_no": request.form['flat_no']
        }
        if tenant:
            tenants_collection.update_one({'_id': ObjectId(tenant_id)}, {'$set': tenant_data})
        else:
            tenants_collection.insert_one(tenant_data)
        return redirect(url_for('index'))
    return render_template('add_tenant.html', tenant=tenant)

@app.route('/receipt/<tenant_id>', methods=['GET', 'POST'])
def generate_receipt(tenant_id):
    tenant = tenants_collection.find_one({'_id': ObjectId(tenant_id)})

    if request.method == 'POST':
        amount_paid = float(request.form['amount_paid'])
        date = datetime.now().strftime('%Y-%m-%d')
        new_dues = tenant['dues_remaining'] - amount_paid
        tenants_collection.update_one(
            {'_id': ObjectId(tenant_id)},
            {'$set': {'dues_remaining': new_dues}}
        )
        tenant = tenants_collection.find_one({'_id': ObjectId(tenant_id)})
        return render_template('receipt.html', tenant=tenant, amount_paid=amount_paid, date=date)
    return render_template('receipt_form.html', tenant=tenant)

@app.route('/delete/<tenant_id>', methods=['POST'])
def delete_tenant(tenant_id):
    tenants_collection.delete_one({'_id': ObjectId(tenant_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=80)
