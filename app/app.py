from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)

questions = [
    {
        "question": "Quelles sont les objets et les produits interdits avant d'accèder à la station ?",
        "options": ["Les objets en verre", "Ustensiles en plastique", " Médicament", "Tomate  et poivrons"],
        "correct_answers": ["Les objets en verre", "Tomate  et poivrons"]
    },
    {
        "question": "Quelles sont les interdictions à l'intérieur de la station ?",
        "options": ["Les bijoux", "Barbe non protégée", "Les produits alimentaires /allergènes", "Les lunettes solaires ou lentilles brisées ou fissurées"],
        "correct_answers": ["Les bijoux", "Barbe non protégée", "Les produits alimentaires /allergènes", "Les lunettes solaires ou lentilles brisées ou fissurées"]
    }
]

@app.route('/')
def home():
    return render_template('quiz.html', questions=questions, enumerate=enumerate)

@app.route('/submit', methods=['POST'])
def submit():
    total_correct = 0
    total_wrong = 0
    total_possible = sum(len(q["correct_answers"]) for q in questions)

    # Retrieve the employee details
    emp_id = request.form.get('emp_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    for i, question in enumerate(questions):
        selected_options = request.form.getlist(f'question-{i}')
        correct_answers = set(question["correct_answers"])
        selected_set = set(selected_options)

        correct_selected = len(correct_answers.intersection(selected_set))
        wrong_selected = len(selected_set - correct_answers)

        total_correct += correct_selected
        total_wrong += wrong_selected

    total_score = total_correct - total_wrong
    success_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0

    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        first_name TEXT,
        last_name TEXT,
        correct INTEGER,
        wrong INTEGER,
        success_percentage REAL
    )
    ''')

    # Insert results into the database
    c.execute('''
    INSERT INTO results (emp_id, first_name, last_name, correct, wrong, success_percentage)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (emp_id, first_name, last_name, total_correct, total_wrong, success_percentage))

    conn.commit()
    conn.close()

    return f'Your score is: {total_correct} correct, {total_wrong} wrong. Success percentage: {success_percentage:.2f}%'

@app.route('/export')
def export():
    conn = sqlite3.connect('quiz_results.db')
    df = pd.read_sql_query("SELECT * FROM results", conn)
    df.to_csv('results.csv', index=False)
    conn.close()
    return 'Results exported to results.csv'

@app.route('/view_results')
def view_results():
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute('SELECT * FROM results')
    rows = c.fetchall()
    conn.close()
    return render_template('view_results.html', results=rows)

@app.route('/boss_view')
def boss_view():
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute('SELECT emp_id, first_name, last_name, SUM(correct), SUM(wrong), AVG(success_percentage) FROM results GROUP BY emp_id')
    rows = c.fetchall()
    conn.close()
    return render_template('boss_view.html', results=rows)

if __name__ == '__main__':
    app.run(debug=True)