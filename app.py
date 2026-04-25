from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ---------------- DATABASE MODEL ----------------
class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle = db.Column(db.String(20))
    violation = db.Column(db.String(50))
    location = db.Column(db.String(50))
    date = db.Column(db.String(50))
    fine = db.Column(db.Integer)
    status = db.Column(db.String(10))


# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------- ADD VIOLATION ----------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        v = request.form['vehicle']
        t = request.form['type']
        l = request.form['location']
        f = int(request.form['fine'])

        # Auto date & time
        d = datetime.now().strftime("%Y-%m-%d %H:%M")

        new = Violation(
            vehicle=v,
            violation=t,
            location=l,
            date=d,
            fine=f,
            status="Unpaid"
        )

        db.session.add(new)
        db.session.commit()

        # Create QR folder if not exists
        if not os.path.exists('static/qr_codes'):
            os.makedirs('static/qr_codes')

        # Generate QR Code
        qr_data = f"http://127.0.0.1:5000/status/{new.id}"
        img = qrcode.make(qr_data)
        img.save(f"static/qr_codes/{new.id}.png")

        return redirect('/')

    return render_template('add.html')


# ---------------- SEARCH ----------------
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        vehicle = request.form['vehicle']
        data = Violation.query.filter_by(vehicle=vehicle).all()

        # Total fine calculation
        total = sum(i.fine for i in data)

        return render_template('result.html', data=data, total=total)

    return render_template('search.html')


# ---------------- MARK AS PAID ----------------
@app.route('/pay/<int:id>')
def pay(id):
    record = Violation.query.get(id)
    record.status = "Paid"
    db.session.commit()
    return redirect('/search')


# ---------------- STATUS PAGE ----------------
@app.route('/status/<int:id>')
def status(id):
    record = Violation.query.get(id)
    return render_template('status.html', record=record)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    if not os.path.exists('database.db'):
        with app.app_context():
            db.create_all()

    app.run(debug=True)