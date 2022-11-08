import json
from . import db
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from .models import User, Stocks, History
import yfinance as yf

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def index():
    stocks = []
    net_worth = 0
    for stock in current_user.stocks:
        tk = yf.Ticker(stock.name)
        data = tk.info
        stock_profile = {
            'name': stock.name,
            'number': stock.number,
            'value': round(stock.number * data['currentPrice'], 2)
        }
        net_worth = round(net_worth + stock_profile['value'], 2)
        stocks.append(stock_profile)
    net_worth = round(net_worth + current_user.cash, 2)
    return jsonify(cash=current_user.cash, stocks=stocks, net_worth=net_worth)


@views.route('/quote', methods=['GET', 'POST'])
@login_required
def quote():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        if not name:
            return jsonify(message="Please enter name", category="error", user=current_user.name)
        else:
            tk = yf.Ticker(name)
            data = tk.info
            if 'currentPrice' not in data:
                return jsonify(message="Not a valid company name", category="error", user=current_user.name)
            else:
                return jsonify(price=data['currentPrice'])
    return jsonify(message="Enter company name", user=current_user.name)


@views.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        quantity = int(data['quantity'])
        if not name:
            return jsonify(message="Enter company name", category="error", user=current_user.name)
        elif not quantity or quantity <= 0:
            return jsonify(message="Enter valid quantity", category="error", user=current_user.name)
        else:
            tk = yf.Ticker(name)
            data = tk.info
            if 'currentPrice' not in data:
                return jsonify(message="Not a valid company name", category="error", user=current_user.name)
            elif current_user.cash < data['currentPrice'] * quantity:
                return jsonify(message="Not enough cash", category="error", user=current_user.name)
            else:
                stock = Stocks.query.filter_by(user_id=current_user.id, name=name).first()
                if stock:
                    stock.number += quantity
                    db.session.commit()
                else:
                    stock = Stocks(user_id=current_user.id, name=name, number=quantity)
                    db.session.add(stock)
                    db.session.commit()
                history = History(user_id=current_user.id, name=name, number=quantity, price=data['currentPrice'])
                current_user.cash = round(current_user.cash - quantity * data['currentPrice'], 2)
                db.session.add(history)
                db.session.commit()
                stocks = []
                for stock in current_user.stocks:
                    stock_profile = {
                    'name': stock.name,
                    'number': stock.number
                    }
                    stocks.append(stock_profile)
                return jsonify(message="Bought!", stocks=stocks, cash=current_user.cash)


@views.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        quantity = int(data['quantity'])
        if not name:
            return jsonify(message="Enter company name", category="error", user= current_user.name)
        elif not quantity or quantity <= 0:
            return jsonify(message="Enter valid quantity", category="error", user=current_user.name)
        else:
            tk = yf.Ticker(name)
            data = tk.info
            stock = Stocks.query.filter_by(user_id= current_user.id, name= name).first()
            if stock.number < quantity:
                return jsonify(message="You do not own that much stock", category="error", user=current_user.name)
            elif stock.number == quantity:
                Stocks.query.filter_by(user_id= current_user.id, name= name).delete()
                current_user.cash = round(current_user.cash + quantity * data['currentPrice'], 2)
                history = History(user_id=current_user.id, name=name, number= -quantity, price=data['currentPrice'])
                db.session.add(history)
            else:
                stock.number -= quantity
                current_user.cash = round(current_user.cash + quantity * data['currentPrice'], 2)
                history = History(user_id=current_user.id, name=name, number= -quantity, price=data['currentPrice'])
                db.session.add(history)
            db.session.commit()
            return jsonify(message="Sold!", category="success")
    stock_names = []
    for stock in current_user.stocks:
        stock_names.append(stock.name)
    return jsonify(user=current_user.name, stock_names=stock_names)


@views.route('/history', methods=['GET'])
@login_required
def history():
    history_total = []
    for history in current_user.history:
        history_profile = {
            'name': history.name,
            'number': history.number,
            'price': history.price,
            'value': round(history.number * history.price, 2),
            'date': str(history.date)
        }
        history_total.append(history_profile)
    return jsonify(user=current_user.name, history=history_total)