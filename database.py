import sqlite3
import bcrypt

DB_FILE = "users.db"

def create_table():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def register_user(email, login, password):
    create_table()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, login, password) VALUES (?, ?, ?)",
                           (email, login, hashed_password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Login lub email już istnieją

def login_user(login, password):
    create_table()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE login = ?", (login,))
        row = cursor.fetchone()

        if row and bcrypt.checkpw(password.encode(), row[0].encode()):
            return True
        return False
