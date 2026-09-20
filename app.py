from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'movie_secret_key_2026'


def get_db():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Пользователь уже существует')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
