from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """User class to store users in the database"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # TODO add secure password field

    def __repr__(self):
        return self.username


class ToDO(db.Model):
    """To-do class to store tasks in the database"""
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), unique=False, nullable=False)
    due_date = db.Column(db.DateTime, unique=False)
    is_completed = db.Column(db.Boolean, unique=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return self.task
