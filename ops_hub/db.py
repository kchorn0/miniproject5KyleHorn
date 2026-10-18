# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles connecting to the SQLite database and creating its tables.

# sqlite3 is Python's built-in library for working with SQLite databases
import sqlite3

# datetime lets us turn saved timestamps back into Python date/time objects
from datetime import datetime

# click is the library Flask uses to make terminal commands (like "flask init-db")
import click

# current_app is the Flask app that is running right now (lets us read its settings)
from flask import current_app

# g is a storage spot that lasts for one request - we keep the database connection here
from flask import g


# Open (or reuse) the database connection for this request
def get_db():
    """Return the database connection for the current request.

    The connection is stored in g, so calling this again during the
    same request reuses it instead of opening a new one.
    """
    # Only open a new connection if this request doesn't have one yet
    if "db" not in g:
        # Open the database file whose path is in the app's DATABASE setting.
        # PARSE_DECLTYPES lets the timestamp converter at the bottom of this file work.
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Lets us read columns by name, like row["name"], instead of by number
        g.db.row_factory = sqlite3.Row
        # SQLite ignores foreign keys unless this is turned on for each connection.
        # Without it, ON DELETE CASCADE / SET NULL in schema.sql would do nothing.
        g.db.execute("PRAGMA foreign_keys = ON")

    # Give back the connection (new or reused)
    return g.db


# e is an error Flask may pass in; we don't need it, but Flask requires the parameter
def close_db(e=None):
    """Close the database connection at the end of the request, if one was opened."""
    # Remove the connection from g. Returns None if no connection was opened.
    db = g.pop("db", None)

    # Only close it if there was one, so we don't waste open connections
    if db is not None:
        db.close()


# Build the tables by running schema.sql
def init_db():
    """Delete any existing data and create fresh tables from schema.sql."""
    # Get a connection to the database
    db = get_db()

    # Open schema.sql (it sits in the ops_hub folder next to this file)
    with current_app.open_resource("schema.sql") as f:
        # Read the file, turn its bytes into text, and run every SQL command in it
        db.executescript(f.read().decode("utf8"))


# Turns the function below into a terminal command named "init-db"
@click.command("init-db")
def init_db_command():
    """Terminal command: flask --app ops_hub init-db"""
    # Build the tables
    init_db()
    # Print a success message in the terminal
    click.echo("Initialized the database.")


# Columns declared as TIMESTAMP are saved as text. This converts that text back
# into a Python datetime object when we read it, so we can format dates in templates.
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


# Called from create_app() in __init__.py to hook the database into the app
def init_app(app):
    """Connect the database functions to the Flask app."""
    # After every request finishes, run close_db() automatically
    app.teardown_appcontext(close_db)
    # Add "init-db" to the list of commands the flask terminal tool understands
    app.cli.add_command(init_db_command)
