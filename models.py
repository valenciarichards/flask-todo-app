from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Setup database configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """User class to store users in the database"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60))
    tasks = db.relationship("Task", backref="user", lazy=True)

    def __repr__(self):
        return f"User: {self.username}, Email: {self.email}"


class Task(db.Model):
    """To-Do class to store tasks in the database"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    due_date = db.Column(db.DateTime, unique=False, nullable=False)
    # Priority will default to 4 (lowest) if none is entered.
    priority = db.Column(db.Integer, unique=False, default=4)
    # Mark tasks as incomplete by default.
    is_completed = db.Column(db.Boolean, unique=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Task: {self.name}, Due: {self.due_date}"
