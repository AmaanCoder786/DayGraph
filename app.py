from flask import Flask, request, redirect, render_template
from datetime import datetime
from database.db import get_db_connection

app = Flask(__name__)


@app.route('/')
def home():
    conn = get_db_connection()
    habits = conn.execute(
        "SELECT * FROM habits ORDER BY id"
    ).fetchall()
    conn.close()
    return render_template('home.html', habits=habits)

@app.route('/habit/<int:habit_id>')
def habit_page(habit_id):
    conn = get_db_connection()

    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?",
        (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Habit not found", 404

    today = datetime.now().date().isoformat()

    entries = conn.execute(
        """
        SELECT * FROM entries
        WHERE habit_id = ? AND date = ?
        ORDER BY created_at
        """,
        (habit_id, today)
    ).fetchall()

    conn.close()

    return render_template(
        'habit.html',
        habit=habit,
        entries=entries
    )

@app.route('/habit/<int:habit_id>/add-entry', methods=['POST'])
def add_entry(habit_id):

    value = request.form['value'].strip()

    try:
        value = float(value)
    except ValueError:
        return "Invalid value", 400

    today = datetime.now().date().isoformat()
    created_at = datetime.now().isoformat(timespec="seconds")

    conn = get_db_connection()
    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?", (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Habit not found", 404

    conn.execute(
        """
        INSERT INTO entries (habit_id, value, date, created_at) VALUES (?, ?, ?, ?)
        """,
        (habit_id, value, today, created_at)
    )
    conn.commit()
    conn.close()

    return redirect(f'/habit/{habit_id}')


@app.route('/add-habit', methods=['GET', 'POST'])
def add_habit():

    if request.method == 'POST':
        name = request.form['name'].strip()
        unit = request.form['unit'].strip()
        direction = request.form['direction']

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO habits (name, unit, direction)
            VALUES (?, ?, ?)
            """,
            (name, unit, direction)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_habit.html')


if __name__ == '__main__':
    app.run(debug=True)