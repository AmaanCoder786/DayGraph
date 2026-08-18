from flask import Flask, request, redirect, render_template, url_for
from datetime import datetime
from database.db import get_db_connection

app = Flask(__name__)

# ============================================================
# HOME PAGE
# ============================================================

@app.route('/')
def home():
    conn = get_db_connection()

    habits = conn.execute(
        "SELECT * FROM habits ORDER BY id"
    ).fetchall()

    habit_data = []

    # Get daily totals for each habit's progress graph
    for habit in habits:
        daily_totals = conn.execute(
            """
            SELECT date, SUM(value) AS total
            FROM entries
            WHERE habit_id = ?
            GROUP BY date
            ORDER BY date ASC
            """,
            (habit['id'],)
        ).fetchall()

        habit_data.append({
            'habit': habit,
            'daily_totals': daily_totals
        })

    conn.close()

    return render_template(
        'home.html',
        habit_data=habit_data
    )

# ============================================================
# INDIVIDUAL HABIT PAGE
# ============================================================

@app.route('/habit/<int:habit_id>')
def habit_page(habit_id):
    conn = get_db_connection()

    # Get the selected habit
    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?",
        (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Habit not found", 404

    today = datetime.now().date().isoformat()

    # Get today's individual entries
    entries = conn.execute(
        """
        SELECT * FROM entries
        WHERE habit_id = ? AND date = ?
        ORDER BY created_at
        """,
        (habit_id, today)
    ).fetchall()

    # Format timestamps for display
    entries = [
        {
            **dict(entry),
            'display_time': datetime.fromisoformat(
                entry['created_at']
            ).strftime('%I:%M %p')
        }
        for entry in entries
    ]

    # Calculate today's total
    total = conn.execute(
        """
        SELECT COALESCE(SUM(value), 0) AS total
        FROM entries
        WHERE habit_id = ? AND date = ?
        """,
        (habit_id, today)
    ).fetchone()['total']

    # Get daily totals for the progress graph
    daily_totals = conn.execute(
        """
        SELECT date, SUM(value) AS total
        FROM entries
        WHERE habit_id = ?
        GROUP BY date
        ORDER BY date ASC
        """,
        (habit_id,)
    ).fetchall()

    conn.close()

    return render_template(
        'habit.html',
        habit=habit,
        entries=entries,
        total=total,
        daily_totals=daily_totals
    )

# ============================================================
# ADD ENTRY TO A HABIT
# ============================================================

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

    # Make sure the habit exists before adding the entry
    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?",
        (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Habit not found", 404

    conn.execute(
        """
        INSERT INTO entries (habit_id, value, date, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (habit_id, value, today, created_at)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('habit_page', habit_id=habit_id))

# ============================================================
# ADD NEW HABIT
# ============================================================

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

        return redirect(url_for('home'))

    return render_template('add_habit.html')

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    app.run(debug=True)