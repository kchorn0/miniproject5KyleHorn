# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles manager accounts: register, log in, log out,
# and protecting pages so only logged-in users can see them.

# functools.wraps keeps a function's name when we wrap it in a decorator (Flask needs the name)
import functools

# Blueprint groups related routes together (all the account pages live in this one)
from flask import Blueprint

# flash shows a one-time message on the next page (displayed by base.html)
from flask import flash

# g stores data for the current request - we put the logged-in user here
from flask import g

# redirect sends the browser to a different page
from flask import redirect

# render_template builds an HTML page from a template file
from flask import render_template

# request holds what the browser sent us, including form data
from flask import request

# session remembers data between requests using a signed cookie (who is logged in)
from flask import session

# url_for builds a URL from a function name
from flask import url_for

# check_password_hash compares a typed password to the saved hash
from werkzeug.security import check_password_hash

# generate_password_hash turns a password into a hash so we never store the real password
from werkzeug.security import generate_password_hash

# get_db gives us the database connection (from our db.py file)
from .db import get_db

# Create the blueprint named "auth". url_prefix="/auth" puts all its URLs under /auth,
# for example /auth/login and /auth/register.
bp = Blueprint("auth", __name__, url_prefix="/auth")


# Decorator: putting @login_required above a route makes that page require login
def login_required(view):
    """Send users who are not logged in to the login page."""

    # wraps(view) copies the original function's name onto wrapped_view
    @functools.wraps(view)
    # **kwargs passes along any URL values (like a student id) to the original view
    def wrapped_view(**kwargs):
        # No one is logged in, so send them to the login page instead
        if g.user is None:
            return redirect(url_for("auth.login"))

        # Someone is logged in, so run the original page function normally
        return view(**kwargs)

    # Return the new protected version of the function
    return wrapped_view


# before_app_request runs this function before EVERY request in the whole app
@bp.before_app_request
def load_logged_in_user():
    """Look up the logged-in user (if any) and store them in g.user."""
    # Get the user's id saved in the session cookie (None if not logged in)
    user_id = session.get("user_id")

    # Not logged in
    if user_id is None:
        g.user = None
    # Logged in: load that user's row from the database so pages can use it
    else:
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        )


# /auth/register page. GET = show the form, POST = the form was submitted.
@bp.route("/register", methods=("GET", "POST"))
def register():
    """Create a new manager account."""
    # Only process the form when it was submitted
    if request.method == "POST":
        # Read the typed values from the form. .strip() removes extra spaces around the username.
        username = request.form["username"].strip()
        password = request.form["password"]
        # Get the database connection
        db = get_db()
        # Start with no error; set one if something is wrong
        error = None

        # Make sure both fields were filled in
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        # Only try to save if there were no errors
        if error is None:
            try:
                # Save the new user. The ? placeholders safely insert the values
                # (this prevents SQL injection). The password is hashed first.
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # commit() actually saves the change to the database file
                db.commit()
            # username is UNIQUE in schema.sql, so a duplicate name causes this error
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # else runs only if the try worked (no error)
            else:
                # Green message on the login page, then send the user there
                flash("Account created. Please log in.", "success")
                return redirect(url_for("auth.login"))

        # Something went wrong: show the error in a red alert
        flash(error, "danger")

    # GET request (or a failed POST): show the register form
    return render_template("auth/register.html")


# /auth/login page. GET = show the form, POST = the form was submitted.
@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in by saving the user's id in the session."""
    # Only process the form when it was submitted
    if request.method == "POST":
        # Read the typed values from the form
        username = request.form["username"].strip()
        password = request.form["password"]
        # Get the database connection
        db = get_db()
        # Start with no error
        error = None
        # Find the user with this username (None if not found)
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        # Use one vague message for both cases so strangers can't
        # find out which usernames exist
        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect username or password."

        # Login worked
        if error is None:
            # Clear any old session data, then remember who is logged in
            session.clear()
            session["user_id"] = user["id"]
            # Send them to the home page
            return redirect(url_for("index"))

        # Login failed: show the error in a red alert
        flash(error, "danger")

    # GET request (or a failed POST): show the login form
    return render_template("auth/login.html")


# /auth/logout - just a link, no form needed
@bp.route("/logout")
def logout():
    """Log out by clearing the session."""
    # Forget everything in the session, including user_id
    session.clear()
    # Blue info message on the login page
    flash("You have been logged out.", "info")
    # Send them to the login page
    return redirect(url_for("auth.login"))
