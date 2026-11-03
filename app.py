import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, redirect, url_for, flash
import helpers

app = Flask(__name__)
app.secret_key = "daa-student-project-secret-2026"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# =========================================================================
# ROUTE 1: ADD DETAILS (Faculty, Students, Rooms, Courses & Generate Schedule)
# =========================================================================
@app.route('/', methods=['GET', 'POST'])
def manage_details():
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))

    if request.method == 'POST':
        action = request.form.get('action', '')

        # 1. ADD STUDENT GROUP
        if action == 'add_group':
            group_id = request.form.get('group_id', '').strip()
            group_name = request.form.get('group_name', '').strip()
            size = request.form.get('size', '').strip()

            ok, err = helpers.validate_group_data(group_id, group_name, size, groups)
            if not ok:
                flash(err, 'error')
            else:
                groups.append({'group_id': group_id, 'group_name': group_name, 'size': size})
                helpers.write_csv(os.path.join(DATA_DIR, 'groups.csv'), ['group_id', 'group_name', 'size'], groups)
                flash(f"Student Group '{group_id}' added successfully!", 'success')
            return redirect(url_for('manage_details'))

        # 2. ADD FACULTY
        elif action == 'add_faculty':
            faculty_id = request.form.get('faculty_id', '').strip()
            name = request.form.get('name', '').strip()
            unavail = request.form.get('unavailable_slots', '').strip() or 'none'

            ok, err = helpers.validate_faculty_data(faculty_id, name, unavail, faculty)
            if not ok:
                flash(err, 'error')
            else:
                faculty.append({'faculty_id': faculty_id, 'name': name, 'unavailable_slots': unavail})
                helpers.write_csv(os.path.join(DATA_DIR, 'faculty.csv'), ['faculty_id', 'name', 'unavailable_slots'], faculty)
                flash(f"Faculty '{name} ({faculty_id})' added successfully!", 'success')
            return redirect(url_for('manage_details'))

        # 3. ADD ROOM
        elif action == 'add_room':
            room_id = request.form.get('room_id', '').strip()
            capacity = request.form.get('capacity', '').strip()
            unavail = request.form.get('unavailable_slots', '').strip() or 'none'

            ok, err = helpers.validate_room_data(room_id, capacity, unavail, rooms)
            if not ok:
                flash(err, 'error')
            else:
                rooms.append({'room_id': room_id, 'capacity': capacity, 'unavailable_slots': unavail})
                helpers.write_csv(os.path.join(DATA_DIR, 'rooms.csv'), ['room_id', 'capacity', 'unavailable_slots'], rooms)
                flash(f"Room '{room_id}' added successfully!", 'success')
            return redirect(url_for('manage_details'))

        # 4. ADD COURSE
        elif action == 'add_course':
            code = request.form.get('course_code', '').strip()
            name = request.form.get('course_name', '').strip()
            f_id = request.form.get('faculty_id', '').strip()
            g_id = request.form.get('group_id', '').strip()
            sessions = request.form.get('sessions_per_week', '').strip()

            ok, err = helpers.validate_course_data(code, name, f_id, g_id, sessions, courses, faculty, groups)
            if not ok:
                flash(err, 'error')
            else:
                courses.append({
                    'course_code': code,
                    'course_name': name,
                    'faculty_id': f_id,
                    'group_id': g_id,
                    'sessions_per_week': sessions
                })
                helpers.write_csv(os.path.join(DATA_DIR, 'courses.csv'), ['course_code', 'course_name', 'faculty_id', 'group_id', 'sessions_per_week'], courses)
                flash(f"Course '{code} - {name}' added successfully!", 'success')
            return redirect(url_for('manage_details'))

        # 5. DELETE ACTIONS
        elif action == 'delete_group':
            del_id = request.form.get('item_id', '').strip()
            if any(c['group_id'] == del_id for c in courses):
                flash(f"Cannot delete group '{del_id}' because courses are assigned to it.", 'error')
            else:
                groups = [g for g in groups if g['group_id'] != del_id]
                helpers.write_csv(os.path.join(DATA_DIR, 'groups.csv'), ['group_id', 'group_name', 'size'], groups)
                flash(f"Group '{del_id}' deleted.", 'info')
            return redirect(url_for('manage_details'))

        elif action == 'delete_faculty':
            del_id = request.form.get('item_id', '').strip()
            if any(c['faculty_id'] == del_id for c in courses):
                flash(f"Cannot delete faculty '{del_id}' because courses are assigned to them.", 'error')
            else:
                faculty = [f for f in faculty if f['faculty_id'] != del_id]
                helpers.write_csv(os.path.join(DATA_DIR, 'faculty.csv'), ['faculty_id', 'name', 'unavailable_slots'], faculty)
                flash(f"Faculty '{del_id}' deleted.", 'info')
            return redirect(url_for('manage_details'))

        elif action == 'delete_room':
            del_id = request.form.get('item_id', '').strip()
            rooms = [r for r in rooms if r['room_id'] != del_id]
            helpers.write_csv(os.path.join(DATA_DIR, 'rooms.csv'), ['room_id', 'capacity', 'unavailable_slots'], rooms)
            flash(f"Room '{del_id}' deleted.", 'info')
            return redirect(url_for('manage_details'))

        elif action == 'delete_course':
            del_id = request.form.get('item_id', '').strip()
            courses = [c for c in courses if c['course_code'] != del_id]
            helpers.write_csv(os.path.join(DATA_DIR, 'courses.csv'), ['course_code', 'course_name', 'faculty_id', 'group_id', 'sessions_per_week'], courses)
            flash(f"Course '{del_id}' deleted.", 'info')
            return redirect(url_for('manage_details'))

        # 6. RUN OPTIMIZATION ALGORITHM (GENERATE SCHEDULE)
        elif action == 'generate':
            ok, msg = helpers.run_scheduler(mode='generate')
            if ok:
                flash("Timetable and Exam Schedule generated successfully using C++ Optimization Engine!", 'success')
                return redirect(url_for('show_details'))
            else:
                flash(f"Scheduler Error: {msg}", 'error')
                return redirect(url_for('manage_details'))

    return render_template(
        'add.html',
        groups=groups,
        faculty=faculty,
        rooms=rooms,
        courses=courses
    )


# =========================================================================
# ROUTE 2: SHOW DETAILS (View All Records, Generated Timetable & Exams)
# =========================================================================
@app.route('/view')
def show_details():
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))

    timetable = helpers.read_csv(os.path.join(OUTPUT_DIR, 'timetable.csv'))
    exams = helpers.read_csv(os.path.join(OUTPUT_DIR, 'exams.csv'))
    summary_raw = helpers.read_csv(os.path.join(OUTPUT_DIR, 'summary.csv'))
    summary = {r['key']: r['value'] for r in summary_raw} if summary_raw else {}
    conflicts = helpers.read_csv(os.path.join(OUTPUT_DIR, 'conflicts.csv'))
    unscheduled = helpers.read_csv(os.path.join(OUTPUT_DIR, 'unscheduled.csv'))

    course_names = {c['course_code']: c['course_name'] for c in courses}
    faculty_names = {f['faculty_id']: f['name'] for f in faculty}
    group_names = {g['group_id']: g['group_name'] for g in groups}

    # Enhance timetable entries
    for item in timetable:
        item['course_name'] = course_names.get(item['course_code'], item['course_code'])
        item['faculty_name'] = faculty_names.get(item['faculty_id'], item['faculty_id'])
        item['group_name'] = group_names.get(item['group_id'], item['group_id'])

    for item in exams:
        item['course_name'] = course_names.get(item['course_code'], item['course_code'])
        item['group_name'] = group_names.get(item['group_id'], item['group_id'])

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    slots = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    # Build weekly grid dictionary: grid[day][slot] = list of classes
    grid = {d: {s: [] for s in slots} for d in days}
    for item in timetable:
        d = item.get('day', '')
        s = item.get('slot', '')
        if d in grid and s in grid[d]:
            grid[d][s].append(item)

    return render_template(
        'view.html',
        groups=groups,
        faculty=faculty,
        rooms=rooms,
        courses=courses,
        timetable=timetable,
        grid=grid,
        days=days,
        slots=slots,
        exams=exams,
        summary=summary,
        conflicts=conflicts,
        unscheduled=unscheduled
    )


if __name__ == '__main__':
    # Auto-generate schedule if not present yet
    if not os.path.exists(os.path.join(OUTPUT_DIR, 'timetable.csv')):
        helpers.run_scheduler('generate')
    app.run(debug=True, port=5000)
