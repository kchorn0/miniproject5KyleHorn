-- Student Operations Hub database
-- Running "flask --app ops_hub init-db" deletes all data and rebuilds these tables.
-- In SQL, two dashes (--) start a comment, like # in Python.

-- Delete the old tables (if they exist) so we start fresh.
-- Child tables are dropped first because they point to the students table.
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS systems;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

-- Manager login accounts
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number for each user, assigned automatically
  username TEXT UNIQUE NOT NULL,         -- required, and no two users can have the same one
  password TEXT NOT NULL                 -- stores a hash of the password, never the real password
);

-- Student employees (records only - they do not log in)
CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number for each student
  name TEXT NOT NULL,                    -- required
  email TEXT,                            -- optional (no NOT NULL)
  role TEXT,                             -- job title, optional
  status TEXT NOT NULL DEFAULT 'Active'  -- required; becomes 'Active' if no value is given
    CHECK (status IN ('Active', 'Inactive')),  -- database rejects any other value
  notes TEXT                             -- optional extra info
);

-- Projects and tasks assigned to a student employee
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number for each project
  title TEXT NOT NULL,                   -- required
  description TEXT,                      -- optional
  student_id INTEGER,                    -- id of the assigned student; can be empty (NULL) = Unassigned
  priority TEXT NOT NULL DEFAULT 'Medium'  -- defaults to Medium
    CHECK (priority IN ('Low', 'Medium', 'High')),  -- only these three are allowed
  due_date TEXT,                         -- saved as text like '2026-10-19' so dates sort correctly
  status TEXT NOT NULL DEFAULT 'Not Started'  -- defaults to Not Started
    CHECK (status IN ('Not Started', 'In Progress', 'Blocked', 'Completed')),  -- allowed statuses
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- date/time the project was added (automatic)
  -- Foreign key: student_id must match an id in the students table.
  -- ON DELETE SET NULL: if that student is deleted, this project stays but becomes Unassigned.
  FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE SET NULL
);

-- Work shifts for student employees
CREATE TABLE schedules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number for each shift
  student_id INTEGER NOT NULL,           -- required: every shift belongs to a student
  shift_date TEXT NOT NULL,              -- date as text, like '2026-10-19'
  start_time TEXT NOT NULL,              -- time as text, like '09:00' (24-hour clock)
  end_time TEXT NOT NULL,                -- time as text, like '13:30'
  notes TEXT,                            -- optional
  -- Foreign key: student_id must match an id in the students table.
  -- ON DELETE CASCADE: if that student is deleted, their shifts are deleted too.
  FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Workplace systems whose status the manager updates by hand (no foreign key needed)
CREATE TABLE systems (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique number for each system
  name TEXT UNIQUE NOT NULL,             -- required, and no duplicate system names
  status TEXT NOT NULL DEFAULT 'Operational'  -- defaults to Operational
    CHECK (status IN ('Operational', 'Degraded', 'Outage')),  -- allowed statuses
  notes TEXT,                            -- short description or current issue
  last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  -- when the status last changed
);

-- Starting systems so the System Status page is not empty.
-- status and last_updated are left out, so they use their DEFAULT values.
INSERT INTO systems (name, notes) VALUES
  ('Blackboard', 'Learning management system'),
  ('Zoom', 'Video meetings and virtual classes'),
  ('Microsoft 365', 'Email, Teams, and Office apps'),
  ('Campus Wi-Fi', 'Wireless network');
