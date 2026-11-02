# Timetable & Examination Scheduling Optimizer

A high-performance academic scheduling system combining a **C++17 greedy & conflict-graph optimization engine** with a modern **Flask web interface**, running locally on Windows.

Built in accordance with the project development plan for **Design & Analysis of Algorithms (DAA)**.

---

## 🌟 Features & Highlights

- **C++17 Engine (`cpp/scheduler.exe`)**:
  - **Greedy Weekly Timetable Scheduler**: Hardest-first course ordering (by weekly sessions, cohort sizes, and faculty unavailability). Multi-pass placement respecting soft preferences (lecture day spreading, best-fit room allocation).
  - **Exam Scheduling via Conflict Graph Coloring**: Courses sharing student cohorts form conflict edges. Welsh-Powell degree ordering heuristic assigns conflict-free examination slots.
  - **Conflict Auditor (`check` mode)**: Self-validates timetable and exam allocations against all hard constraints (faculty clashes, room double-bookings, cohort overlaps, capacity limits, and availability restrictions).
  - **Diagnostic Unscheduled Tracking**: Any unplaced session is recorded with clear explanatory reasons (`room too small`, `faculty unavailable or clash`, `group clash`, `room clash`, etc.).
  - **Sub-5 Millisecond Execution**: Highly optimized zero-allocation C++ with bit-matrix conflict checking.

- **Flask Web Application**:
  - **Executive Dashboard**: Real-time KPI counters, quick generate action, conflict auditor, and architecture overview.
  - **Interactive Entity Management**: Full CRUD (Add / Edit / Delete) for Student Groups, Faculty, Classrooms/Labs, and Courses with dropdown linking and input validation.
  - **Visual Unavailable Slots Picker**: Interactive chip selectors to easily set availability constraints.
  - **Weekly Timetable Grid**: Interactive matrix (Monday–Friday, S1–S6) with instant in-browser filtering by Student Group, Faculty, or Room, plus list view toggle, CSV export, and print styling.
  - **Exam Schedule Visualizer**: Morning (AM) and Afternoon (PM) timeline cards with room badges.
  - **Comprehensive Audit & Report**: Room utilization percentage progress bars, unscheduled breakdown, conflict log, and built-in DAA Viva preparation guide.

---

## 📂 Project Structure

```
c:\Users\iamsu\Documents\Projects\DAA\
├── app.py                     # Flask web server and routes
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
├── templates/                 # HTML5 / Jinja2 Templates
│   ├── base.html              # Layout, glassmorphism navbar, alerts
│   ├── index.html             # Dashboard with KPI cards and architecture
│   ├── groups.html            # Student groups management
│   ├── faculty.html           # Faculty management with visual slot picker
│   ├── rooms.html             # Room inventory with capacity tracking
│   ├── courses.html           # Course catalog and faculty/group assignment
│   ├── timetable.html         # Weekly timetable matrix with live filtering
│   ├── exams.html             # Exam cards grouped by day & session
│   └── report.html            # Room utilization bars & viva prep guide
├── static/                    # Frontend Assets
│   ├── style.css              # Custom styling tokens, dark theme, responsive grid
│   └── app.js                 # Filter interactions, modals, slot picker
└── tests/
    └── test_runner.py         # Automated test suite covering 12 plan test scenarios
```

---

## 🚀 Quick Start Guide

### 1. Compile the C++ Engine
Run `build.bat` in the project root:
```bat
build.bat
```
This compiles `cpp/main.cpp`, `cpp/csv_io.cpp`, `cpp/conflict.cpp`, `cpp/timetable.cpp`, `cpp/exam.cpp`, and `cpp/report.cpp` into `cpp/scheduler.exe` with `-O2` optimizations and static runtime linking.

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

The project includes an automated test runner implementing all 12 test scenarios from Section 10 of the development plan:

```bat
python tests/test_runner.py
```

### Verified Test Cases:
1. **Normal sample data**: All classes placed, 0 conflicts.
2. **Faculty with limited availability**: Correctly places available session and logs unscheduled session (`faculty unavailable or clash`).
3. **Single room bottleneck**: 1 placed, 1 unscheduled (`room clash`).
4. **Group larger than room capacity**: Unscheduled (`room too small`).
5. **Group clash**: Multiple courses for the same group in a single slot are caught (`group clash`).
6. **Faculty unavailable in all slots**: Properly identified and unscheduled (`faculty unavailable`).
7. **Exam slot exhaustion**: 3 exams in 2 slots catches overlap (`no exam slot without overlap`).
8. **Check mode validation**: Planted faculty, room, and group clashes are all detected and reported by `check` mode.
9. **Missing or empty files**: Gracefully returns exit code 1 with clean error description without crashing.
10. **Input validation**: Non-positive sessions rejected by Python validation.
11. **Multi-group exam sharing**: Multiple cohorts share exam slots in different rooms without conflict.
12. **Exam room capacity check**: Room smaller than group is never assigned and logged as unscheduled.

---

## 🧠 DAA Algorithm & Viva Reference

### 1. Greedy Choice Property
At each step, the scheduler places the next highest-priority session in the earliest valid time slot and the smallest fitting room.

### 2. Welsh-Powell Graph Coloring
In exam scheduling:
- Courses are vertices $V$.
- Edges $E$ connect courses with identical student cohorts.
- Vertices are sorted by degree $\deg(v)$ descending.
- Slots are colors assigned greedily, guaranteeing that no student cohort ever has two exams in the same slot.

### 3. Complexity
- **Time**: $O(C \log C + C \cdot S \cdot \text{Slots} \cdot \text{Rooms})$ — runs in under 5 ms for college-sized instances.
- **Space**: $O((\text{Faculty} + \text{Groups} + \text{Rooms}) \times \text{Slots})$ using 2D boolean tables for $O(1)$ constraint checking.
