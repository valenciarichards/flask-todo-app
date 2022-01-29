# forms.py

from flask_wtf import Form
from wtforms import StringField, PasswordField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SignupUserForm(Form):
    """Collect and validate input to signup a user."""
    username = StringField("Username", validators=[DataRequired(), Length(min=6, max=25)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=40)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])


class LoginUserForm(Form):
    """Collect and validate input to login a user."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class AddOrUpdateTaskForm(Form):
    """Collect and validate input to add a task"""
    task_id = IntegerField()
    name = StringField("Task Name", validators=[DataRequired()])
    due_date = DateField("Due Date", validators=[DataRequired()])
    priority = SelectField("Priority", validators=[DataRequired()], coerce=int,
                           choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")])
