# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles the Dashboard (home page): a quick summary of students, projects, and systems.
# It only READS from the database - nothing is added or changed here.

# date lets us get today's date to find overdue and upcoming projects
from datetime import date

# Blueprint groups the dashboard route
from flask import Blueprint

# render_template builds an HTML page from a template file
from flask import render_template

# login_required protects the page so only logged-in users can see it
from .auth import login_required

# get_db gives us the database connection
from .db import get_db

# Reuse the badge colors already defined in projects.py and systems.py (no copying)
from .projects import PRIORITY_COLORS
from .systems import STATUS_COLORS as SYSTEM_COLORS

# Create the blueprint named "dashboard" (no url_prefix, so its page is at "/")
bp = Blueprint("dashboard", __name__)


# "/" - the home page
@bp.route("/")
@login_required
def index():
    """Show summary numbers, upcoming deadlines, and system statuses."""
    # Get the database connection once and reuse it for every query below
    db = get_db()
    # Today's date as text like "2026-10-17" (matches how due dates are saved)
    today = date.today().isoformat()

    # COUNT(*) counts rows. fetchone()[0] grabs the single number from the result.
    # Number of Active student employees
    active_students = db.execute(
        "SELECT COUNT(*) FROM students WHERE status = 'Active'"
    ).fetchone()[0]

    # Number of projects that aren't finished yet
    open_projects = db.execute(
        "SELECT COUNT(*) FROM projects WHERE status != 'Completed'"
    ).fetchone()[0]

    # Number of unfinished projects whose due date has already passed
    overdue_projects = db.execute(
        "SELECT COUNT(*) FROM projects WHERE status != 'Completed' AND due_date < ?",
        (today,),
    ).fetchone()[0]

    # Next 5 unfinished projects due today or later, soonest first.
    # LEFT JOIN adds the student's name (Unassigned projects still show).
    # LIMIT 5 keeps the list short.
    upcoming = db.execute(
        "SELECT p.title, p.priority, p.due_date, s.name AS student_name"
        " FROM projects p LEFT JOIN students s ON p.student_id = s.id"
        " WHERE p.status != 'Completed' AND p.due_date >= ?"
        " ORDER BY p.due_date"
        " LIMIT 5",
        (today,),
    ).fetchall()

    # Every system and its status, alphabetical
    systems = db.execute("SELECT name, status FROM systems ORDER BY name").fetchall()
    # How many systems are not Operational (same idea as the Systems page)
    system_problems = sum(1 for system in systems if system["status"] != "Operational")

    # Send everything to the template
    return render_template(
        "dashboard/index.html",
        active_students=active_students,
        open_projects=open_projects,
        overdue_projects=overdue_projects,
        upcoming=upcoming,
        systems=systems,
        system_problems=system_problems,
        priority_colors=PRIORITY_COLORS,
        system_colors=SYSTEM_COLORS,
    )
