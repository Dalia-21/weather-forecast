from server import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))


class WeatherEntry(db.Model):
    __tablename__ = 'weather_entries'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.String(255))
