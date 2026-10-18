# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 5

# This file handles the Student Employees pages: list, add, edit, and delete.

# Blueprint groups the student routes together
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

# Create the blueprint named "students". All its URLs start with /students.
bp = Blueprint("students", __name__, url_prefix="/students")

# The only status values allowed (they match the CHECK rule in schema.sql).
# Used to build the dropdown menu and to check what the form sent.
STATUSES = ["Active", "Inactive"]


# Helper used by the edit and delete routes to load one student
def get_student(id):
    """Get one student by id, or show a 404 page if it doesn't exist."""
    # Look up the student with this id
    student = get_db().execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

    # No student with that id (for example, someone typed a bad URL)
    if student is None:
        abort(404, f"Student id {id} doesn't exist.")

    # Give back the student's row
    return student


# Helper used by the add and edit routes to read and check the form
def read_student_form():
    """Read the student fields from the submitted form and check them.

    Returns the values and an error message (None if everything is valid).
    Both the add and edit pages use this, so the rules live in one place.
    """
    # .get(..., "") returns "" if a field is missing; .strip() removes extra spaces
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    role = request.form.get("role", "").strip()
    status = request.form.get("status", "")
    notes = request.form.get("notes", "").strip()
    # Start with no error
    error = None

    # Name is the only required text field
    if not name:
        error = "Name is required."
    # Status must be one of the allowed values (protects against edited forms)
    elif status not in STATUSES:
        error = "Please choose a valid status."

    # Return all the values plus the error together
    return name, email, role, status, notes, error


# /students - the list of all student employees
@bp.route("/")
@login_required
def index():
    """Show all student employees in a table, sorted by name."""
    # Get every student, alphabetical by name
    students = get_db().execute("SELECT * FROM students ORDER BY name").fetchall()
    # Send the list to the template so it can build the table
    return render_template("students/index.html", students=students)


# /students/create - GET shows the empty form, POST saves the new student
@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Add a new student employee."""
    # Form was submitted
    if request.method == "POST":
        # Read and check the form fields
        name, email, role, status, notes, error = read_student_form()

        # Something was wrong: show a red message and the form again
        if error is not None:
            flash(error, "danger")
        # Everything is valid: save the new student
        else:
            db = get_db()
            # ? placeholders safely insert the values (prevents SQL injection)
            db.execute(
                "INSERT INTO students (name, email, role, status, notes)"
                " VALUES (?, ?, ?, ?, ?)",
                (name, email, role, status, notes),
            )
            # Save the change to the database file
            db.commit()
            # Green success message, then go back to the list
            flash(f"Student {name} added.", "success")
            return redirect(url_for("students.index"))

    # GET (or a failed POST): show the form. statuses fills the dropdown.
    return render_template("students/create.html", statuses=STATUSES)


# /students/5/update - <int:id> captures the number in the URL and passes it in as id
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Edit an existing student employee."""
    # Load the student (or show 404 if the id doesn't exist)
    student = get_student(id)

    # Form was submitted
    if request.method == "POST":
        # Read and check the form fields
        name, email, role, status, notes, error = read_student_form()

        # Something was wrong: show a red message and the form again
        if error is not None:
            flash(error, "danger")
        # Everything is valid: save the changes
        else:
            db = get_db()
            # UPDATE changes the existing row; WHERE id = ? makes sure only this student changes
            db.execute(
                "UPDATE students SET name = ?, email = ?, role = ?, status = ?, notes = ?"
                " WHERE id = ?",
                (name, email, role, status, notes, id),
            )
            db.commit()
            # Green success message
            flash(f"Student {name} updated.", "success")
            # Go back to the student list
            return redirect(url_for("students.index"))

    # GET (or a failed POST): show the form filled in with the student's current info
    return render_template("students/update.html", student=student, statuses=STATUSES)


# /students/5/delete - POST only, so a delete can't happen just by visiting a link
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a student employee.

    Because of the foreign key in schema.sql (ON DELETE SET NULL),
    their projects stay but become Unassigned.
    """
    # Make sure the student exists (404 if not) and get their name for the message
    student = get_student(id)
    db = get_db()
    # Remove the student's row
    db.execute("DELETE FROM students WHERE id = ?", (id,))
    db.commit()
    # Yellow warning-style message, then back to the list
    flash(f"Student {student['name']} deleted.", "warning")
    return redirect(url_for("students.index"))
