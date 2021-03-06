# app.py

from flask import Flask, redirect, url_for, render_template, request, session, flash
from forms import SignupUserForm, LoginUserForm, AddOrUpdateTaskForm
from models import db, User, Task
from functools import wraps
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

# Create the initial database
db.create_all()

# Setup password hashing
bcrypt = Bcrypt(app)


# Helper functions

def login_required(func):
    """Restrict access to pages that require a user to be logged in."""

    @wraps(func)
    def wrap(*args, **kwargs):
        """Return the given function if the user is logged in. Otherwise, redirect to the login page."""

        if "logged_in" in session:
            return func(*args, **kwargs)
        # Otherwise, prompt the user to login and redirect to the login page.
        else:
            flash("You have to be logged in to access that page.")
            return redirect(url_for("login"))

    return wrap


def verify_task_owner(task_id):
    """Return True if the logged-in user created the given task. Otherwise, show an error and return False.
    """
    task = db.session.query(Task).get_or_404(task_id)
    if task.user_id == session["user_id"]:
        return True
    else:
        flash("You don't have permission to access that page.")
        return False


# Route handlers

@app.route("/")
def index():
    """Redirect to login page."""
    return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Log the user in."""
    error = None
    form = LoginUserForm(request.form)
    if request.method == "POST":
        # Validate form data.
        if form.validate():
            user = db.session.query(User).filter_by(username=form.username.data).first()
            # If the user is in the database and the password is correct, log the user in and redirect to tasks page.
            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
                session["logged_in"] = True
                session["user_id"] = user.id
                session["username"] = user.username
                flash("Welcome back, {}!".format(user.username))
                return redirect(url_for("tasks"))
            # Otherwise, show an error.
            else:
                error = "Invalid username and password combination."
        else:
            error = "Please enter your username and password."
    return render_template("login.html", form=form, error=error)


@app.route("/logout/")
def logout():
    """Log the user out of the app."""
    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have successfully logged out.")
    return redirect(url_for("login"))


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    """Create an account for a new user."""
    error = None
    form = SignupUserForm(request.form)
    if request.method == "POST":
        # Validate form data.
        if form.validate():
            # Create the new User.
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=bcrypt.generate_password_hash(form.password.data),
            )
            # Add the new User to the database and redirect to the login page.
            # Handle database errors.
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Account successfully created. Please sign in.")
                return redirect(url_for("login"))
            except IntegrityError:
                error = "That username and/or email address already exists. Please login."
                return render_template("login.html", form=form, error=error)
        else:
            error = "Account not created. Please correct errors and try again."
    return render_template("signup.html", form=form, error=error)


@app.route("/tasks/")
@app.route("/tasks/<sort_param>")
@login_required
def tasks(sort_param=None):
    """View all tasks by selected sort order and display a form to add tasks."""
    form = AddOrUpdateTaskForm(request.form)
    # If optional sort parameter is passed, sort depending on value.
    # Sort by newest first.
    if sort_param == "by_newest_first":
        items = db.session.query(Task).filter_by(user_id=session["user_id"]).order_by(Task.created_datetime.desc())
    # Sort by earliest due date.
    elif sort_param == "by_earliest_due_date":
        items = db.session.query(Task).filter_by(user_id=session["user_id"]).order_by(Task.due_date.asc())
    # Sort by highest priority.
    elif sort_param == "by_highest_priority":
        items = db.session.query(Task).filter_by(user_id=session["user_id"]).order_by(Task.priority.asc())
    # Sort by oldest first (default)
    else:
        items = db.session.query(Task).filter_by(user_id=session["user_id"]).order_by(Task.created_datetime.asc())

    incomplete_tasks = items.filter_by(is_complete=False)
    complete_tasks = items.filter_by(is_complete=True)

    return render_template("tasks.html", form=form, incomplete_tasks=incomplete_tasks, complete_tasks=complete_tasks)


@app.route("/add/", methods=["GET", "POST"])
@login_required
def add_task():
    """Add a task."""
    form = AddOrUpdateTaskForm(request.form)
    if request.method == "POST":
        # Validate form data.
        if form.validate():
            # Create a new Task.
            new_task = Task(
                name=form.name.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                is_complete=False,
                created_datetime=datetime.now(),
                user_id=session["user_id"]
            )
            # Add the Task to the database and redirect to the tasks page.
            db.session.add(new_task)
            db.session.commit()
            flash("Task successfully added.")
            return redirect(url_for("tasks"))
        else:
            flash("All fields are required.")
            return redirect(url_for("tasks"))

    return render_template("tasks.html", form=form)


@app.route("/edit/<int:task_id>/", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    """Edit the name, due date or priority of a task."""
    if verify_task_owner(task_id):
        # Query database for task to update. If the task does not exist, raise a 404 error.
        task = db.session.query(Task).get_or_404(task_id)
        # Pre-populate the form with current task data.
        form = AddOrUpdateTaskForm(request.form, obj=task)
        if request.method == "POST" and form.validate():
            updated_task = {
                "name": form.name.data,
                "due_date": form.due_date.data,
                "priority": form.priority.data,
            }
            # Update the Task in the database and commit changes.
            db.session.query(Task).filter_by(id=task_id).update(updated_task)
            db.session.commit()
            flash("Task successfully updated.")
        else:
            return render_template("edit_task.html", form=form, task=task)
    return redirect(url_for("tasks"))


@app.route("/complete/<int:task_id>/")
@login_required
def mark_task_as_complete(task_id):
    """Mark a task as complete."""
    if verify_task_owner(task_id):
        db.session.query(Task).filter_by(id=task_id).update({"is_complete": True})
        db.session.commit()
        flash("Marked as complete. Good job!")
    return redirect(url_for("tasks"))


@app.route("/delete/<int:task_id>/")
@login_required
def delete_task(task_id):
    """Delete a task."""
    if verify_task_owner(task_id):
        db.session.query(Task).filter_by(id=task_id).delete()
        db.session.commit()
        flash("Task deleted.")
    return redirect(url_for("tasks"))


if __name__ == "__main__":
    app.run(port=3000)
