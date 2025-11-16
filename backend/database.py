import sqlite3
import os

def get_db_path():
    """Returns the path to the database file."""
    if "PYTEST_CURRENT_TEST" in os.environ:
        return os.path.join(os.path.dirname(__file__), '..', 'dataset', 'test_hr_data.db')
    return os.path.join(os.path.dirname(__file__), '..', 'dataset', 'hr_data.db')

def init_db():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    """)

    # Create attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    """)

    # Create leaves table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    """)

    # Create audit_log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id TEXT,
        action TEXT NOT NULL,
        details TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
