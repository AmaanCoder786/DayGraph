import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / 'database' / 'daygraph.db'


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    # Create a connection to the SQLite database.
    conn = sqlite3.connect(DATABASE)

    # Enable SQLite foreign-key enforcement.
    conn.execute("PRAGMA foreign_keys = ON")

    # Return rows as dictionary-like objects so we can use
    # column names such as row['name'] instead of row[0].
    conn.row_factory = sqlite3.Row

    return conn