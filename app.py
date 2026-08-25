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

    # Get all activities
    habits = conn.execute(
        "SELECT * FROM habits ORDER BY id"
    ).fetchall()

    habit_data = []

    # Get daily totals and today's status for each activity
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

        today = datetime.now().date().isoformat()

        today_total = conn.execute(
            """
            SELECT COALESCE(SUM(value), 0) AS total
            FROM entries
            WHERE habit_id = ? AND date = ?
            """,
            (habit['id'], today)
        ).fetchone()['total']

        today_entry = conn.execute(
            """
            SELECT id
            FROM entries
            WHERE habit_id = ? AND date = ?
            LIMIT 1
            """,
            (habit['id'], today)
        ).fetchone()

        habit_data.append({
            'habit': habit,
            'daily_totals': daily_totals,
            'today_total': today_total,
            'recorded_today': today_entry is not None
        })

    # ========================================================
    # TODAY'S PULSE SUMMARY
    # ========================================================

    activity_count = len(habits)

    entry_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM entries
        WHERE date = ?
        """,
        (today,)
    ).fetchone()[0]

    active_today = conn.execute(
        """
        SELECT COUNT(DISTINCT habit_id)
        FROM entries
        WHERE date = ?
        """,
        (today,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        'home.html',
        habit_data=habit_data,
        activity_count=activity_count,
        entry_count=entry_count,
        active_today=active_today
    )


# ============================================================
# INDIVIDUAL ACTIVITY PAGE
# ============================================================

@app.route('/habit/<int:habit_id>')
def habit_page(habit_id):
    conn = get_db_connection()

    # Get the selected activity
    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?",
        (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Activity not found", 404

    today = datetime.now().date().isoformat()

    # Get today's individual entries
    entries = conn.execute(
        """
        SELECT *
        FROM entries
        WHERE habit_id = ? AND date = ?
        ORDER BY created_at DESC
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
# ADD ENTRY TO AN ACTIVITY
# ============================================================

@app.route('/habit/<int:habit_id>/add-entry', methods=['POST'])
def add_entry(habit_id):
    raw_value = request.form.get('value', '').strip()

    # Make sure a value was submitted
    if not raw_value:
        return "Value is required", 400

    # Convert the submitted value to a number
    try:
        value = float(raw_value)
    except ValueError:
        return "Invalid value", 400

    # Reject negative values
    if value < 0:
        return "Value cannot be negative", 400

    # Reject NaN and infinite values
    if not float('-inf') < value < float('inf'):
        return "Invalid value", 400

    today = datetime.now().date().isoformat()
    created_at = datetime.now().isoformat(timespec="seconds")

    conn = get_db_connection()

    # Make sure the activity exists before adding the entry
    habit = conn.execute(
        "SELECT * FROM habits WHERE id = ?",
        (habit_id,)
    ).fetchone()

    if habit is None:
        conn.close()
        return "Activity not found", 404

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
# ADD NEW ACTIVITY
# ============================================================

@app.route('/add-habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        unit = request.form.get('unit', '').strip()
        direction = request.form.get('direction', '').strip()

        # Validate activity name
        if not name:
            return "Activity name is required", 400

        # Validate unit
        if not unit:
            return "Unit is required", 400

        # Validate direction
        if direction not in ('higher', 'lower'):
            return "Invalid direction", 400

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