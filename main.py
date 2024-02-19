from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import plotly
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
        }

@app.route('/')
def index():
    expenses = Expense.query.all()
    expenses = [e.to_dict() for e in expenses]

    for expense in expenses:
        expense["date"] = expense["date"].split("T")[0]
        
    expenses = sorted(expenses, key=lambda item: item['date'])
    graphJSON = json.dumps(expenses, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON, expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')

        date = datetime.strptime(date, '%Y-%m-%d')

        expense = Expense(category=category, amount=amount, date=date)
        db.session.add(expense)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
