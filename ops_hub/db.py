# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

import sqlite3
from datetime import datetime

import click
from flask import current_app
from flask import g


def get_db():
    """Return the database connection for the current request.

    The connection is stored in g, so calling this again during the
    same request reuses it instead of opening a new one.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Lets us read columns by name, like row["name"]
        g.db.row_factory = sqlite3.Row
        # SQLite ignores foreign keys unless this is turned on for each connection
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request, if one was opened."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Delete any existing data and create fresh tables from schema.sql."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Terminal command: flask --app ops_hub init-db"""
    init_db()
    click.echo("Initialized the database.")


# Turn TIMESTAMP columns into Python datetime objects when they are read
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    """Connect the database functions to the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
