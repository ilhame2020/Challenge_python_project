import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = "dev-secret"
# Optional: limit upload size to 1MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


def add_student(students, name, age, grade):
    students.append({"name": name, "age": age, "grade": grade})


def average_grade(students):
    if not students:
        return 0
    total = sum(student["grade"] for student in students)
    return total / len(students)


def best_student(students):
    if not students:
        return None
    return max(students, key=lambda student: student["grade"])


def failing_students(students, threshold):
    return [student for student in students if student["grade"] < threshold]


def group_by_age(students):
    age_groups = {}
    for student in students:
        age = student["age"]
        age_groups[age] = age_groups.get(age, 0) + 1
    return age_groups


def save_students_to_file(students, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for student in students:
            file.write(f"{student['name']},{student['age']},{student['grade']}\n")


def load_students_from_file(filename):
    students = []
    if not os.path.exists(filename):
        return students
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) != 3:
                continue
            name, age, grade = parts
            try:
                students.append({"name": name, "age": int(age), "grade": float(grade)})
            except ValueError:
                # skip malformed lines
                continue
    return students


# Data file (relative to this file)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'students.txt')

# Load initial data
students = load_students_from_file(DATA_FILE)


@app.route('/')
def index():
    avg = average_grade(students)
    best = best_student(students)
    age_groups = group_by_age(students)
    return render_template('index.html', students=students, avg=avg, best=best, age_groups=age_groups)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            age = int(request.form.get('age', ''))
            grade = float(request.form.get('grade', ''))
        except ValueError:
            flash('Age must be integer and grade must be a number.', 'danger')
            return redirect(url_for('add'))

        if not name:
            flash('Name is required.', 'danger')
            return redirect(url_for('add'))

        add_student(students, name, age, grade)
        # auto-save on add
        save_students_to_file(students, DATA_FILE)
        flash(f'Student {name} added.', 'success')
        return redirect(url_for('index'))

    return render_template('add_student.html')


@app.route('/failing', methods=['GET', 'POST'])
def failing():
    threshold = request.args.get('threshold')
    result = []
    if threshold is not None:
        try:
            t = float(threshold)
            result = failing_students(students, t)
        except ValueError:
            flash('Threshold must be a number.', 'danger')
    return render_template('failing.html', students=result, threshold=threshold)


def parse_students_file_stream(stream):
    """Parse a file-like object with lines 'name,age,grade' and return list of student dicts and count of skipped lines."""
    parsed = []
    skipped = 0
    for raw in stream:
        # raw may be bytes or str depending on stream; normalize
        if isinstance(raw, bytes):
            line = raw.decode('utf-8', errors='ignore').strip()
        else:
            line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 3:
            skipped += 1
            continue
        name, age_s, grade_s = parts
        try:
            age = int(age_s)
            grade = float(grade_s)
            parsed.append({"name": name, "age": age, "grade": grade})
        except ValueError:
            skipped += 1
    return parsed, skipped


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload'))

        # parse file in-memory (stream)
        try:
            parsed, skipped = parse_students_file_stream(file.stream)
        except Exception as e:
            flash('Failed to parse file: ' + str(e), 'danger')
            return redirect(url_for('upload'))

        added = 0
        for s in parsed:
            add_student(students, s['name'], s['age'], s['grade'])
            added += 1

        # save merged list
        save_students_to_file(students, DATA_FILE)
        flash(f'Uploaded: {added} students added, {skipped} lines skipped.', 'success')
        return redirect(url_for('index'))

    return render_template('upload.html')


@app.route('/save')
def save():
    save_students_to_file(students, DATA_FILE)
    flash(f'Students saved to {DATA_FILE}', 'success')
    return redirect(url_for('index'))


@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            name = data['name']
            age = int(data['age'])
            grade = float(data['grade'])
        except (KeyError, ValueError, TypeError):
            return jsonify({"error": "Invalid payload. Expecting name, age, grade."}), 400

        add_student(students, name, age, grade)
        save_students_to_file(students, DATA_FILE)
        return jsonify({"status": "ok"}), 201

    return jsonify(students)


if __name__ == '__main__':
    # Run via: python app.py
    app.run(debug=True)
