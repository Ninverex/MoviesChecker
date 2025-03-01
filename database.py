import sqlite3
from PySide6.QtWidgets import QMessageBox
from werkzeug.security import generate_password_hash, check_password_hash


def create_tables():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        login TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        year INTEGER,
                        genre TEXT,
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')  # Dodanie powiązania z tabelą users

    conn.commit()
    conn.close()


def register_user(email, login, password):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? OR login = ?", (email, login))
    if cursor.fetchone():
        return False

    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (email, login, password) VALUES (?, ?, ?)", (email, login, hashed_password))
    conn.commit()
    conn.close()
    return True


def login_user(login, password):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE login = ?", (login,))
    user = cursor.fetchone()

    conn.close()
    return user and check_password_hash(user[0], password)


def add_movie(title, year, genre):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO movies (title, year, genre) VALUES (?, ?, ?)", (title, year, genre))
    conn.commit()
    conn.close()


def get_movies():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    conn.close()
    return movies


def delete_movie(movie_id):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

create_tables()
