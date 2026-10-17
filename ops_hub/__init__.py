# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file makes the ops_hub folder a Python package and builds the Flask app.

# os lets us build file paths and create folders
import os

# Flask is the class that creates our web application
from flask import Flask

# render_template turns an HTML template in the templates/ folder into a finished page
from flask import render_template


# Application factory: Flask looks for a function named create_app() to build the app.
# test_config lets us pass in different settings (for example, a test database).
def create_app(test_config=None):
    """Create and configure the Student Operations Hub Flask app."""
    # Create the app. __name__ tells Flask where this package lives so it can find
    # the templates and static folders. instance_relative_config=True means private
    # files (like the database) are stored in the instance/ folder.
    app = Flask(__name__, instance_relative_config=True)

    # Set the default settings for the app
    app.config.from_mapping(
        # SECRET_KEY signs the login session cookie so users can't fake being logged in.
        # "dev" is fine for local development only.
        SECRET_KEY="dev",
        # Where the SQLite database file is saved: instance/ops_hub.sqlite
        DATABASE=os.path.join(app.instance_path, "ops_hub.sqlite"),
    )

    # Normal run (not testing)
    if test_config is None:
        # Load instance/config.py if it exists. silent=True means don't crash if it's missing.
        app.config.from_pyfile("config.py", silent=True)
    # Testing: use the settings that were passed in instead
    else:
        app.config.update(test_config)

    # Create the instance/ folder if it doesn't exist yet so the database has a place to go.
    # exist_ok=True means don't error if the folder is already there.
    os.makedirs(app.instance_path, exist_ok=True)

    # Import our db.py file (the "." means "from this same package")
    from . import db

    # Connect the database functions and the "init-db" terminal command to the app
    db.init_app(app)

    # Import auth.py (register/login/logout) and login_required to protect pages
    from . import auth
    from .auth import login_required

    # Register the auth blueprint so its /auth/... routes become part of the app
    app.register_blueprint(auth.bp)

    # Import and register the student employee pages (/students/...)
    from . import students

    app.register_blueprint(students.bp)

    # Import and register the projects and assignments pages (/projects/...)
    from . import projects

    app.register_blueprint(projects.bp)

    # Temporary test route - replaced by the dashboard in a later step.
    # @app.route("/") connects the home page URL to the function below it.
    @app.route("/")
    # Only logged-in users can see this page; others are sent to the login page
    @login_required
    def index():
        # Build home.html (which extends base.html) and send it to the browser
        return render_template("home.html")

    # Hand the finished app back to Flask so it can run it
    return app
