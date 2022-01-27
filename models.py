# models.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Setup database configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """User class to store users in the database"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    # Setup one-to-many relationship
    tasks = db.relationship("Task", backref="user")

    def __init__(self, username, email, password):
        self.username = username
        self. email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.username


class Task(db.Model):
    """To-Do class to store tasks in the database"""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    is_complete = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, due_date, priority, is_complete, user_id):
        self.name = name
        self.due_date = due_date
        self.priority = priority
        self.is_complete = is_complete
        self.user_id = user_id

    def __repr__(self):
        return "<Task: %r>" % self.name
