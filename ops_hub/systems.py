# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles the System Status pages: view all systems and update one system's status.
# Systems are added in schema.sql, so there are no add or delete pages here.

# Blueprint groups the system routes together
from flask import Blueprint

# flash shows a one-time message on the next page
from flask import flash

# redirect sends the browser to a different page
from flask import redirect

# render_template builds an HTML page from a template file
from flask import render_template

# request holds the form data the browser sent
from flask import request

# url_for builds a URL from a function name
from flask import url_for

# abort stops the request and shows an error page (like 404 Not Found)
from werkzeug.exceptions import abort

# login_required protects pages so only logged-in users can see them
from .auth import login_required

# get_db gives us the database connection
from .db import get_db

# Create the blueprint named "systems". All its URLs start with /systems.
bp = Blueprint("systems", __name__, url_prefix="/systems")

# Allowed status values (they match the CHECK rule in schema.sql)
STATUSES = ["Operational", "Getting Updates", "Outage"]

# Bootstrap color for each status: green, yellow, red
STATUS_COLORS = {"Operational": "success", "Getting Updates": "warning", "Outage": "danger"}


# Helper used by the update route to load one system
def get_system(id):
    """Get one system by id, or show a 404 page if it doesn't exist."""
    system = get_db().execute("SELECT * FROM systems WHERE id = ?", (id,)).fetchone()

    # No system with that id
    if system is None:
        abort(404, f"System id {id} doesn't exist.")

    # Give back the system's row
    return system


# /systems - status board for every system
@bp.route("/")
@login_required
def index():
    """Show every system and its current status."""
    # Alphabetical by name
    systems = get_db().execute("SELECT * FROM systems ORDER BY name").fetchall()

    # Count how many systems are NOT Operational, for the summary banner at the top.
    # This is a "generator expression": it adds 1 for each system with a problem.
    problems = sum(1 for system in systems if system["status"] != "Operational")

    # Send the systems, problem count, and colors to the template
    return render_template(
        "systems/index.html",
        systems=systems,
        problems=problems,
        status_colors=STATUS_COLORS,
    )


# /systems/3/update - GET shows the form, POST saves the new status
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Change a system's status and notes."""
    # Load the system (or show 404)
    system = get_system(id)

    # Form was submitted
    if request.method == "POST":
        # Read the form fields
        status = request.form.get("status", "")
        notes = request.form.get("notes", "").strip()

        # Status must be one of the allowed values
        if status not in STATUSES:
            flash("Please choose a valid status.", "danger")
        else:
            db = get_db()
            # Save the new status and notes, and set last_updated to the current local time
            db.execute(
                "UPDATE systems SET status = ?, notes = ?,"
                " last_updated = datetime('now', 'localtime')"
                " WHERE id = ?",
                (status, notes, id),
            )
            # Save the change to the database file
            db.commit()
            # Green success message
            flash(f"{system['name']} status set to {status}.", "success")
            # Go back to the status board
            return redirect(url_for("systems.index"))

    # GET (or a failed POST): show the form filled in with the current status
    return render_template(
        "systems/update.html",
        system=system,
        statuses=STATUSES,
        status_colors=STATUS_COLORS,
    )
