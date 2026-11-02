import os
import csv
import subprocess
import re

SCHEDULER_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cpp', 'scheduler.exe')
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

def run_scheduler(mode='generate', data_dir=DATA_DIR, output_dir=OUTPUT_DIR):
    """
    Executes the C++ scheduler binary in generate or check mode.
    Returns (success: bool, message: str).
    """
    if not os.path.exists(SCHEDULER_EXE):
        return False, f"Scheduler executable not found at {SCHEDULER_EXE}. Please run build.bat first."

    os.makedirs(output_dir, exist_ok=True)

    try:
        result = subprocess.run(
            [SCHEDULER_EXE, mode, data_dir, output_dir],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or f"Process exited with code {result.returncode}"
            return False, err
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Scheduler timed out after 60 seconds."
    except Exception as e:
        return False, str(e)

def read_csv(path):
    """
    Reads a CSV file into a list of dictionaries. Returns [] if file does not exist or empty.
    """
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]
    except Exception as e:
        print(f"Error reading CSV {path}: {e}")
        return []

def write_csv(path, fieldnames, rows):
    """
    Writes a list of dictionaries into a CSV file with given headers.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # Only include fields in fieldnames
            filtered = {k: r.get(k, '') for k in fieldnames}
            writer.writerow(filtered)

def validate_slot_string(slot_str):
    """
    Validates slot syntax like MON-S1, WED-S2, or 'none' / empty.
    """
    if not slot_str or slot_str.strip().lower() in ('none', ''):
        return True
    slots = slot_str.split(';')
    valid_pattern = re.compile(r'^(MON|TUE|WED|THU|FRI|SAT|SUN)-S[1-9][0-9]?$', re.IGNORECASE)
    for s in slots:
        s = s.strip()
        if not s or s.lower() == 'none':
            continue
        if not valid_pattern.match(s):
            return False
    return True

def validate_group_data(group_id, name, size_str, existing_groups, is_edit=False, orig_id=None):
    if not group_id or not group_id.strip():
        return False, "Group ID cannot be empty."
    group_id = group_id.strip()
    if not name or not name.strip():
        return False, "Group name cannot be empty."
    try:
        size = int(size_str)
        if size <= 0:
            return False, "Group size must be a positive integer (> 0)."
    except (ValueError, TypeError):
        return False, "Group size must be a valid positive number."

    if not is_edit or (is_edit and group_id != orig_id):
        if any(g['group_id'].lower() == group_id.lower() for g in existing_groups):
            return False, f"Group with ID '{group_id}' already exists."

    return True, ""

def validate_faculty_data(faculty_id, name, unavail_str, existing_faculty, is_edit=False, orig_id=None):
    if not faculty_id or not faculty_id.strip():
        return False, "Faculty ID cannot be empty."
    faculty_id = faculty_id.strip()
    if not name or not name.strip():
        return False, "Faculty name cannot be empty."
    if unavail_str and not validate_slot_string(unavail_str):
        return False, "Invalid slot format in unavailable slots. Example: MON-S1;WED-S2 or none."

    if not is_edit or (is_edit and faculty_id != orig_id):
        if any(f['faculty_id'].lower() == faculty_id.lower() for f in existing_faculty):
            return False, f"Faculty with ID '{faculty_id}' already exists."

    return True, ""

def validate_room_data(room_id, capacity_str, unavail_str, existing_rooms, is_edit=False, orig_id=None):
    if not room_id or not room_id.strip():
        return False, "Room ID cannot be empty."
    room_id = room_id.strip()
    try:
        cap = int(capacity_str)
        if cap <= 0:
            return False, "Room capacity must be a positive integer (> 0)."
    except (ValueError, TypeError):
        return False, "Room capacity must be a valid positive number."
    if unavail_str and not validate_slot_string(unavail_str):
        return False, "Invalid slot format in unavailable slots. Example: MON-S1;WED-S2 or none."

    if not is_edit or (is_edit and room_id != orig_id):
        if any(r['room_id'].lower() == room_id.lower() for r in existing_rooms):
            return False, f"Room with ID '{room_id}' already exists."

    return True, ""

def validate_course_data(code, name, faculty_id, group_id, sessions_str, existing_courses, faculty_list, group_list, is_edit=False, orig_code=None):
    if not code or not code.strip():
        return False, "Course code cannot be empty."
    code = code.strip()
    if not name or not name.strip():
        return False, "Course name cannot be empty."
    if not faculty_id or not any(f['faculty_id'] == faculty_id for f in faculty_list):
        return False, f"Selected faculty '{faculty_id}' does not exist."
    if not group_id or not any(g['group_id'] == group_id for g in group_list):
        return False, f"Selected student group '{group_id}' does not exist."
    try:
        sessions = int(sessions_str)
        if sessions <= 0:
            return False, "Sessions per week must be a positive integer (> 0)."
    except (ValueError, TypeError):
        return False, "Sessions per week must be a valid positive integer."

    if not is_edit or (is_edit and code != orig_code):
        if any(c['course_code'].lower() == code.lower() for c in existing_courses):
            return False, f"Course with code '{code}' already exists."

    return True, ""
