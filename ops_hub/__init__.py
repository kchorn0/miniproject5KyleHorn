# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure the Student Operations Hub Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    # Default settings. SECRET_KEY signs the login session cookie;
    # "dev" is fine for local development only.
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "ops_hub.sqlite"),
    )

    if test_config is None:
        # Load instance/config.py if it exists (lets you override SECRET_KEY)
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    # Make sure the instance folder exists so the database can be created there
    os.makedirs(app.instance_path, exist_ok=True)

    # Temporary test route - replaced by the dashboard in a later step
    @app.route("/")
    def index():
        return "Student Operations Hub is running!!"

    return app
