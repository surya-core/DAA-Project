import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import helpers

app = Flask(__name__)
app.secret_key = "timetabling-optimizer-secret-key-2026"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

def get_stats():
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    
    summary = helpers.read_csv(os.path.join(OUTPUT_DIR, 'summary.csv'))
    summary_dict = {row['key']: row['value'] for row in summary} if summary else {}
    
    timetable = helpers.read_csv(os.path.join(OUTPUT_DIR, 'timetable.csv'))
    exams = helpers.read_csv(os.path.join(OUTPUT_DIR, 'exams.csv'))
    unscheduled = helpers.read_csv(os.path.join(OUTPUT_DIR, 'unscheduled.csv'))
    conflicts = helpers.read_csv(os.path.join(OUTPUT_DIR, 'conflicts.csv'))

    return {
        'num_groups': len(groups),
        'num_faculty': len(faculty),
        'num_rooms': len(rooms),
        'num_courses': len(courses),
        'classes_scheduled': summary_dict.get('classes_scheduled', str(len(timetable))),
        'classes_unscheduled': summary_dict.get('classes_unscheduled', str(len([u for u in unscheduled if u.get('type') == 'class']))),
        'exams_scheduled': summary_dict.get('exams_scheduled', str(len(exams))),
        'exams_unscheduled': summary_dict.get('exams_unscheduled', str(len([u for u in unscheduled if u.get('type') == 'exam']))),
        'conflicts': summary_dict.get('conflicts', str(len(conflicts))),
        'runtime_ms': summary_dict.get('runtime_ms', '0.00'),
        'has_schedule': os.path.exists(os.path.join(OUTPUT_DIR, 'timetable.csv'))
    }

@app.context_processor
def inject_global_stats():
    return {'stats': get_stats()}

@app.route('/')
def index():
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    recent_classes = helpers.read_csv(os.path.join(OUTPUT_DIR, 'timetable.csv'))[:6]
    return render_template(
        'index.html',
        groups=groups,
        faculty=faculty,
        rooms=rooms,
        courses=courses,
        recent_classes=recent_classes
    )

# ----------------- GROUPS -----------------
@app.route('/groups')
def list_groups():
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    return render_template('groups.html', groups=groups)

@app.route('/groups/add', methods=['POST'])
def add_group():
    group_id = request.form.get('group_id', '').strip()
    name = request.form.get('group_name', '').strip()
    size = request.form.get('size', '').strip()

    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    ok, err = helpers.validate_group_data(group_id, name, size, groups)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_groups'))

    groups.append({'group_id': group_id, 'group_name': name, 'size': size})
    helpers.write_csv(os.path.join(DATA_DIR, 'groups.csv'), ['group_id', 'group_name', 'size'], groups)
    flash(f"Group '{group_id}' added successfully.", 'success')
    return redirect(url_for('list_groups'))

@app.route('/groups/edit', methods=['POST'])
def edit_group():
    orig_id = request.form.get('orig_id', '').strip()
    group_id = request.form.get('group_id', '').strip()
    name = request.form.get('group_name', '').strip()
    size = request.form.get('size', '').strip()

    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    ok, err = helpers.validate_group_data(group_id, name, size, groups, is_edit=True, orig_id=orig_id)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_groups'))

    for g in groups:
        if g['group_id'] == orig_id:
            g['group_id'] = group_id
            g['group_name'] = name
            g['size'] = size
            break

    helpers.write_csv(os.path.join(DATA_DIR, 'groups.csv'), ['group_id', 'group_name', 'size'], groups)
    flash(f"Group '{group_id}' updated successfully.", 'success')
    return redirect(url_for('list_groups'))

@app.route('/groups/delete/<group_id>', methods=['POST'])
def delete_group(group_id):
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    
    # Check if used in courses
    if any(c['group_id'] == group_id for c in courses):
        flash(f"Cannot delete group '{group_id}' because courses are assigned to it. Remove or reassign those courses first.", 'warning')
        return redirect(url_for('list_groups'))

    groups = [g for g in groups if g['group_id'] != group_id]
    helpers.write_csv(os.path.join(DATA_DIR, 'groups.csv'), ['group_id', 'group_name', 'size'], groups)
    flash(f"Group '{group_id}' deleted successfully.", 'info')
    return redirect(url_for('list_groups'))

# ----------------- FACULTY -----------------
@app.route('/faculty')
def list_faculty():
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    return render_template('faculty.html', faculty=faculty)

@app.route('/faculty/add', methods=['POST'])
def add_faculty():
    f_id = request.form.get('faculty_id', '').strip()
    name = request.form.get('name', '').strip()
    unavail = request.form.get('unavailable_slots', '').strip() or 'none'

    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    ok, err = helpers.validate_faculty_data(f_id, name, unavail, faculty)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_faculty'))

    faculty.append({'faculty_id': f_id, 'name': name, 'unavailable_slots': unavail})
    helpers.write_csv(os.path.join(DATA_DIR, 'faculty.csv'), ['faculty_id', 'name', 'unavailable_slots'], faculty)
    flash(f"Faculty '{f_id} - {name}' added successfully.", 'success')
    return redirect(url_for('list_faculty'))

@app.route('/faculty/edit', methods=['POST'])
def edit_faculty():
    orig_id = request.form.get('orig_id', '').strip()
    f_id = request.form.get('faculty_id', '').strip()
    name = request.form.get('name', '').strip()
    unavail = request.form.get('unavailable_slots', '').strip() or 'none'

    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    ok, err = helpers.validate_faculty_data(f_id, name, unavail, faculty, is_edit=True, orig_id=orig_id)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_faculty'))

    for f in faculty:
        if f['faculty_id'] == orig_id:
            f['faculty_id'] = f_id
            f['name'] = name
            f['unavailable_slots'] = unavail
            break

    helpers.write_csv(os.path.join(DATA_DIR, 'faculty.csv'), ['faculty_id', 'name', 'unavailable_slots'], faculty)
    flash(f"Faculty '{f_id}' updated successfully.", 'success')
    return redirect(url_for('list_faculty'))

@app.route('/faculty/delete/<f_id>', methods=['POST'])
def delete_faculty(f_id):
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))

    if any(c['faculty_id'] == f_id for c in courses):
        flash(f"Cannot delete faculty '{f_id}' because courses are assigned to them.", 'warning')
        return redirect(url_for('list_faculty'))

    faculty = [f for f in faculty if f['faculty_id'] != f_id]
    helpers.write_csv(os.path.join(DATA_DIR, 'faculty.csv'), ['faculty_id', 'name', 'unavailable_slots'], faculty)
    flash(f"Faculty '{f_id}' deleted successfully.", 'info')
    return redirect(url_for('list_faculty'))

# ----------------- ROOMS -----------------
@app.route('/rooms')
def list_rooms():
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/add', methods=['POST'])
def add_room():
    r_id = request.form.get('room_id', '').strip()
    capacity = request.form.get('capacity', '').strip()
    unavail = request.form.get('unavailable_slots', '').strip() or 'none'

    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    ok, err = helpers.validate_room_data(r_id, capacity, unavail, rooms)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_rooms'))

    rooms.append({'room_id': r_id, 'capacity': capacity, 'unavailable_slots': unavail})
    helpers.write_csv(os.path.join(DATA_DIR, 'rooms.csv'), ['room_id', 'capacity', 'unavailable_slots'], rooms)
    flash(f"Room '{r_id}' added successfully.", 'success')
    return redirect(url_for('list_rooms'))

@app.route('/rooms/edit', methods=['POST'])
def edit_room():
    orig_id = request.form.get('orig_id', '').strip()
    r_id = request.form.get('room_id', '').strip()
    capacity = request.form.get('capacity', '').strip()
    unavail = request.form.get('unavailable_slots', '').strip() or 'none'

    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    ok, err = helpers.validate_room_data(r_id, capacity, unavail, rooms, is_edit=True, orig_id=orig_id)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_rooms'))

    for r in rooms:
        if r['room_id'] == orig_id:
            r['room_id'] = r_id
            r['capacity'] = capacity
            r['unavailable_slots'] = unavail
            break

    helpers.write_csv(os.path.join(DATA_DIR, 'rooms.csv'), ['room_id', 'capacity', 'unavailable_slots'], rooms)
    flash(f"Room '{r_id}' updated successfully.", 'success')
    return redirect(url_for('list_rooms'))

@app.route('/rooms/delete/<r_id>', methods=['POST'])
def delete_room(r_id):
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    rooms = [r for r in rooms if r['room_id'] != r_id]
    helpers.write_csv(os.path.join(DATA_DIR, 'rooms.csv'), ['room_id', 'capacity', 'unavailable_slots'], rooms)
    flash(f"Room '{r_id}' deleted successfully.", 'info')
    return redirect(url_for('list_rooms'))

# ----------------- COURSES -----------------
@app.route('/courses')
def list_courses():
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    return render_template('courses.html', courses=courses, faculty=faculty, groups=groups)

@app.route('/courses/add', methods=['POST'])
def add_course():
    code = request.form.get('course_code', '').strip()
    name = request.form.get('course_name', '').strip()
    f_id = request.form.get('faculty_id', '').strip()
    g_id = request.form.get('group_id', '').strip()
    sessions = request.form.get('sessions_per_week', '').strip()

    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))

    ok, err = helpers.validate_course_data(code, name, f_id, g_id, sessions, courses, faculty, groups)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_courses'))

    courses.append({
        'course_code': code,
        'course_name': name,
        'faculty_id': f_id,
        'group_id': g_id,
        'sessions_per_week': sessions
    })
    helpers.write_csv(os.path.join(DATA_DIR, 'courses.csv'), ['course_code', 'course_name', 'faculty_id', 'group_id', 'sessions_per_week'], courses)
    flash(f"Course '{code} - {name}' added successfully.", 'success')
    return redirect(url_for('list_courses'))

@app.route('/courses/edit', methods=['POST'])
def edit_course():
    orig_code = request.form.get('orig_code', '').strip()
    code = request.form.get('course_code', '').strip()
    name = request.form.get('course_name', '').strip()
    f_id = request.form.get('faculty_id', '').strip()
    g_id = request.form.get('group_id', '').strip()
    sessions = request.form.get('sessions_per_week', '').strip()

    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))

    ok, err = helpers.validate_course_data(code, name, f_id, g_id, sessions, courses, faculty, groups, is_edit=True, orig_code=orig_code)
    if not ok:
        flash(err, 'danger')
        return redirect(url_for('list_courses'))

    for c in courses:
        if c['course_code'] == orig_code:
            c['course_code'] = code
            c['course_name'] = name
            c['faculty_id'] = f_id
            c['group_id'] = g_id
            c['sessions_per_week'] = sessions
            break

    helpers.write_csv(os.path.join(DATA_DIR, 'courses.csv'), ['course_code', 'course_name', 'faculty_id', 'group_id', 'sessions_per_week'], courses)
    flash(f"Course '{code}' updated successfully.", 'success')
    return redirect(url_for('list_courses'))

@app.route('/courses/delete/<course_code>', methods=['POST'])
def delete_course(course_code):
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    courses = [c for c in courses if c['course_code'] != course_code]
    helpers.write_csv(os.path.join(DATA_DIR, 'courses.csv'), ['course_code', 'course_name', 'faculty_id', 'group_id', 'sessions_per_week'], courses)
    flash(f"Course '{course_code}' deleted successfully.", 'info')
    return redirect(url_for('list_courses'))

# ----------------- GENERATE & CHECK -----------------
@app.route('/generate', methods=['POST'])
def generate_schedule():
    ok, msg = helpers.run_scheduler(mode='generate')
    if ok:
        flash("Schedules generated and verified successfully with C++ engine!", 'success')
        return redirect(url_for('view_timetable'))
    else:
        flash(f"Scheduler execution error: {msg}", 'danger')
        return redirect(url_for('index'))

@app.route('/check', methods=['POST'])
def check_schedule():
    ok, msg = helpers.run_scheduler(mode='check')
    conflicts = helpers.read_csv(os.path.join(OUTPUT_DIR, 'conflicts.csv'))
    if len(conflicts) == 0:
        flash("Audit complete: All hard constraints satisfied (0 conflicts detected).", 'success')
    else:
        flash(f"Audit warning: {len(conflicts)} conflict(s) detected! Check details on the Report page.", 'danger')
    return redirect(url_for('view_report'))

# ----------------- RESULTS PAGES -----------------
@app.route('/timetable')
def view_timetable():
    timetable = helpers.read_csv(os.path.join(OUTPUT_DIR, 'timetable.csv'))
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    faculty = helpers.read_csv(os.path.join(DATA_DIR, 'faculty.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))

    course_names = {c['course_code']: c['course_name'] for c in courses}
    faculty_names = {f['faculty_id']: f['name'] for f in faculty}
    group_names = {g['group_id']: g['group_name'] for g in groups}

    # Enhance timetable entries
    for item in timetable:
        item['course_name'] = course_names.get(item['course_code'], item['course_code'])
        item['faculty_name'] = faculty_names.get(item['faculty_id'], item['faculty_id'])
        item['group_name'] = group_names.get(item['group_id'], item['group_id'])

    # Build weekly grid: days = [Mon, Tue, Wed, Thu, Fri], slots = [S1, S2, S3, S4, S5, S6]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    slots = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

    return render_template(
        'timetable.html',
        timetable=timetable,
        days=days,
        slots=slots,
        groups=groups,
        faculty=faculty,
        rooms=rooms
    )

@app.route('/exams')
def view_exams():
    exams = helpers.read_csv(os.path.join(OUTPUT_DIR, 'exams.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    groups = helpers.read_csv(os.path.join(DATA_DIR, 'groups.csv'))
    rooms = helpers.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))

    course_names = {c['course_code']: c['course_name'] for c in courses}
    group_names = {g['group_id']: g['group_name'] for g in groups}

    for item in exams:
        item['course_name'] = course_names.get(item['course_code'], item['course_code'])
        item['group_name'] = group_names.get(item['group_id'], item['group_id'])

    # Group exams by day and session
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    sessions = ['AM', 'PM']

    return render_template(
        'exams.html',
        exams=exams,
        days=days,
        sessions=sessions,
        courses=courses,
        groups=groups,
        rooms=rooms
    )

@app.route('/report')
def view_report():
    summary_raw = helpers.read_csv(os.path.join(OUTPUT_DIR, 'summary.csv'))
    summary = {r['key']: r['value'] for r in summary_raw} if summary_raw else {}

    unscheduled = helpers.read_csv(os.path.join(OUTPUT_DIR, 'unscheduled.csv'))
    conflicts = helpers.read_csv(os.path.join(OUTPUT_DIR, 'conflicts.csv'))
    courses = helpers.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    course_names = {c['course_code']: c['course_name'] for c in courses}

    for u in unscheduled:
        u['course_name'] = course_names.get(u['course_code'], u['course_code'])

    # Parse room utilizations
    room_util = []
    for k, v in summary.items():
        if k.startswith('room_utilization_'):
            r_id = k.replace('room_utilization_', '')
            # format: "23.3% (7/30 slots)"
            pct = 0.0
            try:
                pct = float(v.split('%')[0])
            except:
                pass
            room_util.append({'room_id': r_id, 'display': v, 'pct': pct})

    return render_template(
        'report.html',
        summary=summary,
        unscheduled=unscheduled,
        conflicts=conflicts,
        room_util=room_util
    )

@app.route('/export/<filename>')
def export_file(filename):
    allowed = ['timetable.csv', 'exams.csv', 'unscheduled.csv', 'conflicts.csv', 'summary.csv']
    if filename not in allowed:
        flash("Invalid file export requested.", "danger")
        return redirect(url_for('index'))
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        flash(f"{filename} does not exist yet. Please generate the schedule first.", "warning")
        return redirect(url_for('index'))
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Auto-generate on first run if output doesn't exist
    if not os.path.exists(os.path.join(OUTPUT_DIR, 'timetable.csv')):
        helpers.run_scheduler('generate')
    app.run(debug=True, port=5000)
