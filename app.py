from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        year INTEGER NOT NULL,
        rating REAL DEFAULT 0
    )''')
    cur = conn.execute("SELECT COUNT(*) FROM movies")
    if cur.fetchone()[0] == 0:
        movies = [
            ('Побег из Шоушенка', 'Драма', 1994, 9.3),
            ('Крёстный отец', 'Криминал', 1972, 9.2),
            ('Тёмный рыцарь', 'Боевик', 2008, 9.0),
            ('Криминальное чтиво', 'Криминал', 1994, 8.9),
            ('Форрест Гамп', 'Драма', 1994, 8.8),
            ('Начало', 'Фантастика', 2010, 8.8),
            ('Матрица', 'Фантастика', 1999, 8.7),
            ('Интерстеллар', 'Фантастика', 2014, 8.6),
            ('Бойцовский клуб', 'Триллер', 1999, 8.8),
            ('Гладиатор', 'Боевик', 2000, 8.5),
        ]
        conn.executemany("INSERT INTO movies (title, genre, year, rating) VALUES (?, ?, ?, ?)", movies)
    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db()
    movies = conn.execute("SELECT * FROM movies ORDER BY rating DESC").fetchall()
    conn.close()
    return render_template('index.html', movies=movies)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)