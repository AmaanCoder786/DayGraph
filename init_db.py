import sqlite3

DATABASE = 'database/daygraph.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    direction TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    value REAL NOT NULL,
    
    FOREIGN KEY (habit_id) REFERENCES habits (id)
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")