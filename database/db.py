import sqlite3


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE = 'database/daygraph.db'


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    # Create a connection to the SQLite database.
    conn = sqlite3.connect(DATABASE)

    # Return rows as dictionary-like objects so we can use
    # column names such as row['name'] instead of row[0].
    conn.row_factory = sqlite3.Row

    return conn