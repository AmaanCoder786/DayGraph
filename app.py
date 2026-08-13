from flask import Flask, request, redirect, render_template
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
        "SELECT * FROM habits WHERE id = ?", (habit_id,)
    ).fetchone()

    conn.close()

    if habit is None:
        return "Habit not found", 404

    return render_template('habit.html', habit=habit)


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