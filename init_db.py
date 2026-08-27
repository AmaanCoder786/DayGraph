import sqlite3
from pathlib import Path

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'database' / 'daygraph.db'


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect(DATABASE)
conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
cursor = conn.cursor()


# ============================================================
# HABITS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    direction TEXT NOT NULL
)
""")


# ============================================================
# ENTRIES TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    value REAL NOT NULL,
    created_at TEXT NOT NULL,

    -- Connect each entry to the habit it belongs to.
    FOREIGN KEY (habit_id) REFERENCES habits (id)
)
""")


# ============================================================
# SAVE DATABASE CHANGES
# ============================================================

conn.commit()
conn.close()

print("Database initialized successfully.")