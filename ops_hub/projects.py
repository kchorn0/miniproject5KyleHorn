# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles the Projects and Assignments pages: list, add, edit, and delete.

# date lets us get today's date (to spot overdue projects) and check typed dates
from datetime import date

# Blueprint groups the project routes together
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

# Create the blueprint named "projects". All its URLs start with /projects.
bp = Blueprint("projects", __name__, url_prefix="/projects")

# Allowed values (they match the CHECK rules in schema.sql)
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Not Started", "In Progress", "Blocked", "Completed"]

# Bootstrap badge color for each value, so the templates can color-code them.
# A dictionary maps a key (like "High") to a value (like "danger" = red).
PRIORITY_COLORS = {"Low": "secondary", "Medium": "warning", "High": "danger"}
STATUS_COLORS = {
    "Not Started": "secondary",
    "In Progress": "primary",
    "Blocked": "danger",
    "Completed": "success",
}


def get_project(id):
    """Get one project (with its student's name), or show a 404 page if it doesn't exist."""
    # LEFT JOIN adds the student's name from the students table.
    # "LEFT" keeps the project even if it has no student (Unassigned).
    project = (
        get_db()
        .execute(
            "SELECT p.*, s.name AS student_name"
            " FROM projects p LEFT JOIN students s ON p.student_id = s.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    # No project with that id
    if project is None:
        abort(404, f"Project id {id} doesn't exist.")

    # Give back the project's row
    return project


def get_student_choices():
    """Get every student (id, name, status) for the "Assigned To" dropdown."""
    return get_db().execute("SELECT id, name, status FROM students ORDER BY name").fetchall()


def read_project_form():
    """Read the project fields from the submitted form and check them.

    Returns a dictionary of values and an error message (None if everything is valid).
    """
    # Read each field; .strip() removes extra spaces
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    # The dropdown sends the student's id as text, or "" for Unassigned
    student_id = request.form.get("student_id", "")
    priority = request.form.get("priority", "")
    due_date = request.form.get("due_date", "")
    status = request.form.get("status", "")
    # Start with no error
    error = None

    # Title is required
    if not title:
        error = "Title is required."
    # Priority and status must be allowed values
    elif priority not in PRIORITIES:
        error = "Please choose a valid priority."
    elif status not in STATUSES:
        error = "Please choose a valid status."

    # Unassigned: store NULL (None in Python) in the database
    if student_id == "":
        student_id = None
    # Otherwise make sure it's a real student id
    elif error is None:
        # Look up the student; fetchone() returns None if no student has that id
        found = get_db().execute(
            "SELECT id FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if found is None:
            error = "Please choose a valid student."

    # Due date is optional. If given, make sure it's a real date like 2026-10-19.
    if due_date == "":
        due_date = None
    elif error is None:
        try:
            # fromisoformat raises ValueError if the text isn't a valid YYYY-MM-DD date
            date.fromisoformat(due_date)
        except ValueError:
            error = "Please enter a valid due date."

    # Put the values in a dictionary so we can pass them around as one item
    values = {
        "title": title,
        "description": description,
        "student_id": student_id,
        "priority": priority,
        "due_date": due_date,
        "status": status,
    }
    return values, error


# /projects - list of all projects
@bp.route("/")
@login_required
def index():
    """Show all projects with who they're assigned to."""
    # LEFT JOIN brings in the student's name (Unassigned projects still show).
    # ORDER BY:
    #   p.status = 'Completed'  -> unfinished work first (False sorts before True)
    #   p.due_date IS NULL      -> projects with a due date before ones without
    #   p.due_date              -> soonest due date first
    projects = get_db().execute(
        "SELECT p.*, s.name AS student_name"
        " FROM projects p LEFT JOIN students s ON p.student_id = s.id"
        " ORDER BY p.status = 'Completed', p.due_date IS NULL, p.due_date"
    ).fetchall()

    # today as text like "2026-10-19". Dates saved this way compare correctly as text,
    # so the template can check due_date < today to mark overdue projects.
    return render_template(
        "projects/index.html",
        projects=projects,
        today=date.today().isoformat(),
        priority_colors=PRIORITY_COLORS,
        status_colors=STATUS_COLORS,
    )


# /projects/create - GET shows the empty form, POST saves the new project
@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Add a new project and assign it to a student."""
    # Form was submitted
    if request.method == "POST":
        # Read and check the form fields
        values, error = read_project_form()

        # Something was wrong: show a red message and the form again
        if error is not None:
            flash(error, "danger")
        # Everything is valid: save the new project
        else:
            db = get_db()
            # :title, :description, etc. are named placeholders filled from the values dictionary
            db.execute(
                "INSERT INTO projects (title, description, student_id, priority, due_date, status)"
                " VALUES (:title, :description, :student_id, :priority, :due_date, :status)",
                values,
            )
            db.commit()
            flash(f"Project \"{values['title']}\" added.", "success")
            return redirect(url_for("projects.index"))

    # GET (or a failed POST): show the form with the dropdown choices
    return render_template(
        "projects/create.html",
        students=get_student_choices(),
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


# /projects/5/update - edit an existing project (this is also how you change its status)
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Edit a project, including changing its status."""
    # Load the project (or show 404)
    project = get_project(id)

    # Form was submitted
    if request.method == "POST":
        # Read and check the form fields
        values, error = read_project_form()

        if error is not None:
            flash(error, "danger")
        else:
            # Add the id to the dictionary so the WHERE clause can use :id
            values["id"] = id
            db = get_db()
            db.execute(
                "UPDATE projects SET title = :title, description = :description,"
                " student_id = :student_id, priority = :priority,"
                " due_date = :due_date, status = :status"
                " WHERE id = :id",
                values,
            )
            db.commit()
            flash(f"Project \"{values['title']}\" updated.", "success")
            return redirect(url_for("projects.index"))

    # GET (or a failed POST): show the form filled in with the project's current info
    return render_template(
        "projects/update.html",
        project=project,
        students=get_student_choices(),
        priorities=PRIORITIES,
        statuses=STATUSES,
    )


# /projects/5/delete - POST only, so a delete can't happen just by visiting a link
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a project."""
    # Make sure it exists (404 if not) and get its title for the message
    project = get_project(id)
    db = get_db()
    db.execute("DELETE FROM projects WHERE id = ?", (id,))
    db.commit()
    flash(f"Project \"{project['title']}\" deleted.", "warning")
    return redirect(url_for("projects.index"))
