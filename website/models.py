from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique= True)
    password = db.Column(db.String(150))
    cash = db.Column(db.Float)
    stocks = db.relationship('Stocks')
    history = db.relationship('History')

class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(10), unique=True)
    number = db.Column(db.Integer)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(10))
    number = db.Column(db.Integer)
    price = db.Column(db.Float)
    date = db.Column(db.DateTime(timezone=True), default= func.now())