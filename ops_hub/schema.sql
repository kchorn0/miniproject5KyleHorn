-- Student Operations Hub database
-- Running "flask --app ops_hub init-db" deletes all data and rebuilds these tables.

-- Drop child tables first, because they point to the students table
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS systems;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

-- Manager login accounts (password is stored as a hash, never plain text)
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Student employees (records only - they do not log in)
CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT,
  role TEXT,
  status TEXT NOT NULL DEFAULT 'Active'
    CHECK (status IN ('Active', 'Inactive')),
  notes TEXT
);

-- Projects and tasks assigned to a student employee.
-- If the student is deleted, student_id becomes NULL ("Unassigned").
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  student_id INTEGER,
  priority TEXT NOT NULL DEFAULT 'Medium'
    CHECK (priority IN ('Low', 'Medium', 'High')),
  due_date TEXT,
  status TEXT NOT NULL DEFAULT 'Not Started'
    CHECK (status IN ('Not Started', 'In Progress', 'Blocked', 'Completed')),
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE SET NULL
);

-- Work shifts. If the student is deleted, their shifts are deleted too.
-- Dates are stored as 'YYYY-MM-DD' and times as 'HH:MM'.
CREATE TABLE schedules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  shift_date TEXT NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Workplace systems whose status the manager updates by hand
CREATE TABLE systems (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL DEFAULT 'Operational'
    CHECK (status IN ('Operational', 'Degraded', 'Outage')),
  notes TEXT,
  last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Starting systems so the System Status page is not empty
INSERT INTO systems (name, notes) VALUES
  ('Blackboard', 'Learning management system'),
  ('Zoom', 'Video meetings and virtual classes'),
  ('Microsoft 365', 'Email, Teams, and Office apps'),
  ('Campus Wi-Fi', 'Wireless network');
