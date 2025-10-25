from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = 'exam_secret_key'

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="66520",  # Replace with your MySQL password
    database="exam_proctoring_system"
)
cursor = db.cursor(dictionary=True)

# Template filter
@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s)
    except:
        return []

# Home Page
@app.route('/')
def home():
    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()
    return render_template('home.html', exams=exams)

# Create Exam
@app.route('/create_exam', methods=['GET', 'POST'])
def create_exam():
    if request.method == 'POST':
        try:
            title = request.form['title']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

            if start_dt >= end_dt:
                flash("Start time must be before end time.", "error")
                return redirect(url_for('create_exam'))

            duration = int((end_dt - start_dt).total_seconds() / 60)

            # Insert exam
            cursor.execute(
                "INSERT INTO exams (title, start_time, end_time, duration) VALUES (%s, %s, %s, %s)",
                (title, start_dt, end_dt, duration)
            )
            db.commit()
            exam_id = cursor.lastrowid

            # Insert questions
            for i in range(1, 1000):
                q_text = request.form.get(f'q{i}_text')
                if not q_text:
                    continue

                q_type = request.form.get(f'q{i}_type')
                q_marks = int(request.form.get(f'q{i}_marks', 1))
                q_negative = int(request.form.get(f'q{i}_negative', 0))
                q_difficulty = request.form.get(f'q{i}_difficulty') or None

                options = []
                correct = []

                if q_type == 'mcq':
                    for j in range(1, 5):
                        opt = request.form.get(f'q{i}_option{j}')
                        if opt:
                            options.append(opt)
                            if f'q{i}_correct{j}' in request.form:
                                correct.append(opt)
                elif q_type == 'truefalse':
                    ans = request.form.get(f'q{i}_truefalse')
                    options = ["True", "False"]
                    correct = [ans] if ans else []

                cursor.execute(
                    "INSERT INTO questions (exam_id, q_text, q_type, marks, negative, difficulty, options, correct) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (exam_id, q_text, q_type, q_marks, q_negative, q_difficulty,
                     json.dumps(options), json.dumps(correct))
                )
            db.commit()
            flash("✅ Exam created successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Error creating exam: {e}", "error")
            return redirect(url_for('create_exam'))

    return render_template('create_exam.html')


# Edit Exam
@app.route('/edit_exam/<int:exam_id>', methods=['GET', 'POST'])
def edit_exam(exam_id):
    cursor.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cursor.fetchone()
    if not exam:
        flash("Exam not found.", "error")
        return redirect(url_for('home'))

    cursor.execute("SELECT * FROM questions WHERE exam_id=%s", (exam_id,))
    questions = cursor.fetchall()

    if request.method == 'POST':
        try:
            title = request.form['title']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

            if start_dt >= end_dt:
                flash("Start time must be before end time.", "error")
                return redirect(url_for('edit_exam', exam_id=exam_id))

            duration = int((end_dt - start_dt).total_seconds() / 60)

            # Update exam info
            cursor.execute(
                "UPDATE exams SET title=%s, start_time=%s, end_time=%s, duration=%s WHERE id=%s",
                (title, start_dt, end_dt, duration, exam_id)
            )
            db.commit()

            # Update questions
            for i, q in enumerate(questions, start=1):
                q_text = request.form.get(f'q{i}_text')
                if not q_text:
                    continue
                q_type = request.form.get(f'q{i}_type')
                q_marks = int(request.form.get(f'q{i}_marks', 1))
                q_negative = int(request.form.get(f'q{i}_negative', 0))
                q_difficulty = request.form.get(f'q{i}_difficulty') or None

                options = []
                correct = []

                if q_type == 'mcq':
                    for j in range(1, 5):
                        opt = request.form.get(f'q{i}_option{j}')
                        if opt:
                            options.append(opt)
                            if f'q{i}_correct{j}' in request.form:
                                correct.append(opt)
                elif q_type == 'truefalse':
                    ans = request.form.get(f'q{i}_truefalse')
                    options = ["True", "False"]
                    correct = [ans] if ans else []

                cursor.execute(
                    "UPDATE questions SET q_text=%s, q_type=%s, marks=%s, negative=%s, difficulty=%s, options=%s, correct=%s WHERE id=%s",
                    (q_text, q_type, q_marks, q_negative, q_difficulty,
                     json.dumps(options), json.dumps(correct), q['id'])
                )
            db.commit()
            flash("✅ Exam updated successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Error updating exam: {e}", "error")
            return redirect(url_for('edit_exam', exam_id=exam_id))

    return render_template('edit_exam.html', exam=exam, questions=questions)


# View Exam
@app.route('/view_exam/<int:exam_id>')
def view_exam(exam_id):
    cursor.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cursor.fetchone()
    cursor.execute("SELECT * FROM questions WHERE exam_id=%s", (exam_id,))
    questions = cursor.fetchall()
    return render_template('view_exam.html', exam=exam, questions=questions)


# Instructions Page
@app.route('/instructions/<int:exam_id>')
def instructions(exam_id):
    cursor.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cursor.fetchone()
    if not exam:
        flash("Exam not found.", "error")
        return redirect(url_for('home'))
    return render_template('instructions.html', exam=exam)


# Take Exam
@app.route('/take_exam/<int:exam_id>', methods=['GET', 'POST'])
def take_exam(exam_id):
    cursor.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cursor.fetchone()
    if not exam:
        flash("Exam not found.", "error")
        return redirect(url_for('home'))

    cursor.execute("SELECT * FROM questions WHERE exam_id=%s", (exam_id,))
    questions = cursor.fetchall()

    duration_seconds = (exam.get('duration') or 0) * 60

    if request.method == 'POST':
        score = 0
        total = 0
        results = []

        for q in questions:
            correct_answers = json.loads(q['correct']) if q.get('correct') else []
            user_answer = request.form.get(f'question_{q["id"]}')
            marks = q.get('marks') or 0
            negative = q.get('negative') or 0
            total += marks

            if user_answer and user_answer in correct_answers:
                score += marks
                result = {"question": q['q_text'], "your_answer": user_answer, "status": "✅ Correct"}
            elif user_answer:
                score -= negative
                result = {"question": q['q_text'], "your_answer": user_answer, "status": "❌ Wrong"}
            else:
                result = {"question": q['q_text'], "your_answer": "Not answered", "status": "⚠️ Skipped"}
            results.append(result)

        flash(f"Exam Submitted! You scored {score} out of {total}.", "success")
        return render_template('result.html', exam=exam, results=results, score=score, total=total)

    return render_template('take_exam.html', exam=exam, questions=questions, duration_seconds=duration_seconds)


# Delete Exam
@app.route('/delete_exam/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    cursor.execute("DELETE FROM exams WHERE id=%s", (exam_id,))
    cursor.execute("DELETE FROM questions WHERE exam_id=%s", (exam_id,))
    db.commit()
    flash("Exam deleted successfully!", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
