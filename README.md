# Timetable & Examination Scheduling Optimizer

A college scheduling system combining a **C++17 greedy & conflict-graph optimization engine** with a **Flask web interface**, running locally on Windows.

Built for the **Design & Analysis of Algorithms (DAA)** project.

---

## 🌟 Features & Highlights

- **C++17 Engine (`cpp/scheduler.exe`)**:
  - **Greedy Weekly Timetable Scheduler**: Hardest-first course ordering (by weekly sessions, cohort sizes, and faculty unavailability). Multi-pass placement respecting soft preferences (lecture day spreading, best-fit room allocation).
  - **Exam Scheduling via Conflict Graph Coloring**: Courses sharing student cohorts form conflict edges. Welsh-Powell degree ordering heuristic assigns conflict-free examination slots.
  - **Conflict Auditor**: Validates allocations against hard constraints (faculty clashes, room double-bookings, cohort overlaps, capacity limits).
  - **Sub-5 Millisecond Execution**: Highly optimized C++ algorithm.

- **Flask Web Interface (2 Direct Routes)**:
  - **Route 1 (`/`) - Add Details & Run Engine**:
    - Add/delete Student Groups, Faculty members, Classrooms/Labs, and Courses with validation.
    - One-click trigger to execute the C++ optimization algorithm and generate schedules.
  - **Route 2 (`/view`) - View Schedule & Records**:
    - Master Weekly Timetable Grid (Monday–Friday, Slots 1–6).
    - Examination Schedule table with AM/PM session allocations.
    - Full list of all registered student, faculty, room, and course records.
    - Quick print support (`window.print()`).

---

## 📂 Project Structure

```
c:\Users\iamsu\Documents\Projects\DAA\
├── app.py                     # Flask web server (2 clean routes: / and /view)
├── helpers.py                 # CSV I/O, Python validation, C++ subprocess caller
├── requirements.txt           # Python dependencies (flask)
├── build.bat                  # Compiles C++ engine with g++
├── run.bat                    # Convenience launcher for Windows
├── README.md                  # Project documentation
├── cpp/                       # C++17 Core Optimization Engine
│   ├── main.cpp               # CLI entry point (generate / check)
│   ├── models.h               # Data structures (Group, Faculty, Room, Course, Config)
│   ├── csv_io.h / .cpp        # CSV parsing and output writers
│   ├── conflict.h / .cpp      # canPlace() and checkAll() validation logic
│   ├── timetable.h / .cpp     # Greedy class scheduling algorithm
│   ├── exam.h / .cpp          # Conflict graph construction & Welsh-Powell coloring
│   ├── report.h / .cpp        # Room utilization and KPI summary computation
│   └── scheduler.exe          # Compiled standalone native executable
├── data/                      # Input CSV Data Files
│   ├── config.csv             # Days, slots per day, exam days/sessions
│   ├── groups.csv             # Student groups and cohort sizes
│   ├── faculty.csv            # Instructors and unavailable slots
│   ├── rooms.csv              # Classrooms, labs, and capacities
│   └── courses.csv            # Academic courses, instructors, cohorts, session loads
├── output/                    # Generated Schedules & Diagnostics
│   ├── timetable.csv          # Weekly class schedule
│   ├── exams.csv              # Exam session schedule
│   ├── unscheduled.csv        # Diagnostic unplaced sessions with reasons
│   ├── conflicts.csv          # Audit conflict log
│   └── summary.csv            # Engine metrics, runtime, and room utilization
├── templates/                 # HTML5 Templates (2 main routes)
│   ├── add.html               # Route 1: Add faculty, students, rooms, courses
│   └── view.html              # Route 2: Master weekly timetable, exams, & records
├── static/                    # Frontend Assets
│   ├── style.css              # Student project stylesheet
│   └── app.js                 # Frontend scripts
└── tests/
    └── test_runner.py         # Automated test suite (12 scenarios)
```

---

## 🚀 Quick Start Guide

### 1. Compile the C++ Engine
Run `build.bat` in the project root:
```bat
build.bat
```

### 2. Run the Web Application
Double-click `run.bat` or run:
```bat
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated Test Suite (12 Scenarios)
Run the automated test runner:
```bat
python tests/test_runner.py
```
All 12 test scenarios test edge cases (room over-capacity, faculty unavailability, double booking detection, degree ordering graph coloring, etc.).
