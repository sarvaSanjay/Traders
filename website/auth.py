from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, login_user, logout_user
from .models import User
from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify

auth = Blueprint('auth', __name__)

@auth.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        password = data['password']
        user = User.query.filter_by(name=name).first()
        if not user:
            return jsonify(message="Invalid username", category="error")
        elif not check_password_hash(user.password, password):
            return jsonify(message="Incorrect password", category="error")
        else:
            login_user(user=user, remember=True)
            stocks = []
            for stock in current_user.stocks:
                stock_profile = {
                'name': stock.name,
                'number': stock.number
                }
                stocks.append(stock_profile)
            return jsonify(message="Login Successful", category="succcess", name=current_user.name, stocks=stocks)
    return "Enter login details"

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message="Logged out successfully", category="success")

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        password1 = data['password']
        password2 = data['confirm-password']
        user = User.query.filter_by(name=name).first()
    
        if user:
            return jsonify(message="Username already taken", category="error")
        elif len(name) < 4:
            return jsonify(message="Username must be longer than 4 letters", category="error")
        elif password1 != password2:
            return jsonify(message="Passwords do not match", category="error")
        elif len(password1) <= 7:
            return jsonify(message="Password must be longer than 7 characters", category="error")
        else:
            new_user = User(name=name, password= generate_password_hash(password1), cash = 10000)
            db.session.add(new_user)
            db.session.commit()
            login_user(user=new_user, remember=True)
            return jsonify(message="Signup successful", category="success", user=current_user.name)
    return "Enter signup details"
