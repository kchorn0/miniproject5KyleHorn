# miniproject5KyleHorn

INF601 - Advanced Programming in Python
Kyle Horn
Mini Project 5

## Student Operations Hub

A Flask web application that gives a manager one place to organize student employees, assign and track projects, and monitor the status of important workplace systems.

## Description

Student Operations Hub is a simple internal management dashboard. After registering and logging in, the manager can:

- **See an overview** on the Dashboard: active students, open and overdue projects, upcoming deadlines, and system statuses.
- **Manage student employees:** add, view, edit, and delete records (name, email, role, Active/Inactive status, notes). Student employees are records only; they do not log in.
- **Assign projects and tasks** to students with a priority (Low/Medium/High), due date, and status (Not Started, In Progress, Blocked, Completed). Overdue projects are highlighted in red.
- **Monitor workplace systems** (Blackboard, Zoom, TigernetID/CAS, Workday, Panopto) and update each one's status by hand: Operational (green), Getting Updates (yellow), or Outage (red).

The app is built with Flask, Jinja templates, SQLite, and Bootstrap 5, following the structure of the official Flask tutorial (application factory + blueprints).

### Pages

| Page | URL | What it does |
|---|---|---|
| Register | `/auth/register` | Create a manager account (form, GET/POST) |
| Log In | `/auth/login` | Log in (form, GET/POST) |
| Dashboard | `/` | Summary cards, next 5 deadlines, system statuses |
| Student Employees | `/students/` | Table of all student employees |
| Add / Edit Student | `/students/create`, `/students/<id>/update` | Forms (GET/POST); Delete opens a Bootstrap confirmation modal |
| Projects & Assignments | `/projects/` | Table of projects, who they're assigned to, priority, due date, status |
| Add / Edit Project | `/projects/create`, `/projects/<id>/update` | Forms (GET/POST); status is changed here; Delete opens a Bootstrap modal |
| System Status | `/systems/` | Status board with color-coded cards |
| Update System | `/systems/<id>/update` | Form (GET/POST) to change a system's status and notes |

All pages except Register and Log In require login. Every page extends a shared `base.html` layout with a Bootstrap navbar and flash-message alerts.

### Database

SQLite database with four tables (defined in `ops_hub/schema.sql`):

| Table | Purpose |
|---|---|
| `users` | Manager login accounts (passwords are stored as secure hashes, never plain text) |
| `students` | Student employee records |
| `projects` | Projects/tasks; `student_id` is a **foreign key** to `students.id` |
| `systems` | Workplace systems and their current status |

**Relationship:** one student can have many projects. If a student is deleted, their projects are kept and become "Unassigned" (`ON DELETE SET NULL`).

## Project structure

```
miniproject5KyleHorn/
├── ops_hub/
│   ├── __init__.py          application factory (create_app) and blueprint registration
│   ├── db.py                database connection and the init-db command
│   ├── schema.sql           table definitions and the starting systems
│   ├── auth.py              register, log in, log out, login_required
│   ├── dashboard.py         Dashboard (home page)
│   ├── students.py          student employee pages
│   ├── projects.py          project and assignment pages
│   ├── systems.py           system status pages
│   ├── static/
│   │   └── style.css        small custom styles on top of Bootstrap
│   └── templates/
│       ├── base.html        shared layout: Bootstrap, navbar, flash alerts
│       ├── auth/            login.html, register.html
│       ├── dashboard/       index.html
│       ├── students/        index.html, create.html, update.html
│       ├── projects/        index.html, create.html, update.html
│       └── systems/         index.html, update.html
├── instance/                created automatically; holds ops_hub.sqlite (not in Git)
├── requirements.txt         Python packages needed to run the app
├── .gitignore
└── README.md
```

## Getting Started

### Dependencies

- Python 3.10 or newer (developed and tested on Python 3.14.7)
- pip (comes with Python)
- Flask 3.1 and its helper packages, installed from `requirements.txt` below
- An internet connection when viewing pages (Bootstrap 5.3 loads from the jsDelivr CDN)
- No API keys or environment variables are needed
- Works on Windows (PowerShell) and Linux/macOS (bash); commands for both are given below

### Installing

1. **Clone the repository**

   Windows (PowerShell) and Linux/macOS (bash), same command:
   ```
   git clone https://github.com/kchorn0/miniproject5KyleHorn.git
   cd miniproject5KyleHorn
   ```

2. **Create a virtual environment**

   Windows (PowerShell):
   ```
   python -m venv .venv
   ```
   Linux/macOS (bash):
   ```
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**

   Windows (PowerShell):
   ```
   .\.venv\Scripts\Activate.ps1
   ```
   Linux/macOS (bash):
   ```
   source .venv/bin/activate
   ```
   Your prompt should now start with `(.venv)`.

4. **Install the required packages**
   ```
   pip install -r requirements.txt
   ```

### Initializing the database

Run this once before the first launch (from the project's root folder, with the venv activated):
```
flask --app ops_hub init-db
```
You should see `Initialized the database.` This creates `instance/ops_hub.sqlite` with empty tables plus five starting systems.

⚠️ Running `init-db` again **erases all data** (accounts, students, projects) and starts fresh.

### Executing program

1. Start the development server:
   ```
   flask --app ops_hub run --debug
   ```
2. Open **http://127.0.0.1:5000** in your browser.
3. You'll be sent to the Log In page. Click **Register**, create an account, then log in.
4. Use the navbar to move between pages:
   - **Students:** click *Add Student* to add employees; *Edit* to change them; *Delete* (on the edit page) opens a confirmation modal.
   - **Projects:** click *Add Project*, pick a student from the *Assigned To* dropdown, and set priority, due date, and status. To update progress, click *Edit* and change the status.
   - **Systems:** click *Update* on any card to change its status and notes.
   - **Dashboard:** summarizes everything above.
5. Press **Ctrl+C** in the terminal to stop the server.

## Help

- **`running scripts is disabled on this system`** (Windows only): PowerShell is blocking `Activate.ps1`. Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once in your own PowerShell, or skip activation and use `.\.venv\Scripts\flask.exe --app ops_hub ...` instead.
- **`'flask' is not recognized`** / **`flask: command not found`**: the venv isn't activated or the packages weren't installed. Re-do steps 3 and 4 of Installing.
- **`Could not locate a Flask application`** / **`No module named ops_hub`**: you're not in the project's root folder. `cd` into `miniproject5KyleHorn` (the folder that contains `ops_hub/`).
- **`sqlite3.OperationalError: no such table`**: the database hasn't been created. Run `flask --app ops_hub init-db`.
- **`Address already in use`** / port 5000 busy: run on another port with `flask --app ops_hub run --debug --port 5001`.
- **Pages look plain / unstyled:** Bootstrap loads from the internet; check your connection.

## Notes

- **Development settings:** the app uses `SECRET_KEY="dev"` and Flask's development server, which is fine for running locally but not for a public website. To override the key, create `instance/config.py` containing `SECRET_KEY = "your-random-value"`.
- **Open registration:** anyone who can reach the app can register an account. That fits this class project; a real deployment would restrict or approve new accounts.
- **Scope decision:** a student shift-scheduling feature was planned at first but removed during development to keep the project focused and manageable.

## Authors

Kyle Horn (kchorn@mail.fhsu.edu)

## Acknowledgments

- INF601 Mini Project 5 assignment and requirements (instructor-provided)
- [Flask tutorial](https://flask.palletsprojects.com/en/stable/tutorial/): project structure, application factory, database, and login patterns
- [Flask documentation](https://flask.palletsprojects.com/) and [Jinja documentation](https://jinja.palletsprojects.com/)
- [Bootstrap 5.3 documentation](https://getbootstrap.com/docs/5.3/): navbar, cards, tables, badges, alerts, and modals
- [SQLite documentation](https://www.sqlite.org/docs.html): foreign keys and `datetime('now', 'localtime')`
- Claude Code by Anthropic: the AI coding assistant used to help build this project

## AI Usage

This project was built with Claude Code (Claude Opus 5.5) working as an agent, under my direction. I set the rules for how we worked: one small step at a time, explain each step before writing code, and wait for my approval.

### What Claude did

- Reviewed the assignment rubric and the Flask tutorial, then proposed a step-by-step plan and a checklist mapping each requirement to a part of the app.
- Wrote the Python, SQL, Jinja/HTML, and CSS for each step after explaining what it would build and why, following the tutorial's patterns (application factory, blueprints, `get_db()`, `login_required`).
- Added comments.
- Tested each step with automated checks and a browser preview on a temporary database, and fixed the small issues its tests found (for example, a banner that said "1 system need attention").

### What I did

- Chose the app idea (Student Operations Hub) and defined its purpose, pages, fields, and the single-manager login design.
- Approved or rejected every step before it was built, and asked questions about anything I didn't understand, such as page counts, foreign keys, and options for approving new registrations.
- Created the GitHub repository and made every commit and push myself, writing my own commit messages.
- Ran the app after every step and tested it myself: registering and logging in, adding/editing/deleting students and projects, updating system statuses, and checking the dashboard.
- Made the scope decisions that kept the project finishable and explainable (see below).
- Reviewed and edited the README and wrote this AI Usage section.

### What AI did that I changed

- **Removed the Student Schedules feature.** Claude's plan included a schedules page with its own table. Partway through, I decided the project was getting too complex to explain well and had it removed completely: the table, navbar link, and every reference to it.
- **Replaced the starting systems.** Claude's first version seeded generic systems (Microsoft 365, Campus Wi-Fi). I replaced them with the systems my workplace actually uses: Blackboard, Zoom, TigernetID/CAS, Workday, and Panopto.
- **Renamed a status.** I changed the yellow system status from "Degraded" to "Getting Updates" to match how we describe it at work.
- **Required line-by-line comments.** The first code Claude wrote had only light comments. I had it go back and comment every file so I could explain each line, and kept that rule for all later code.
- **Kept the Dashboard simple.** I asked for a simple dashboard instead of a more complex one, so it only reads and summarizes data.
- **Trimmed the plan.** I approved a reduced scope early on (for example, systems are update-only with no add/delete pages) so the app stayed manageable.
