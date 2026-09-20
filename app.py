from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'movie_secret_key_2026'


def get_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movies.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
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


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/')
def index():
    conn = get_db()
    show_fav = request.args.get('fav') == '1'
    user_id = session.get('user_id', 0)

    if show_fav and 'user_id' in session:
        movies = conn.execute('''SELECT m.*, 1 AS is_fav FROM movies m
            JOIN favorites f ON m.id = f.movie_id
            WHERE f.user_id = ?
            ORDER BY m.rating DESC''', (user_id,)).fetchall()
    else:
        movies = conn.execute('''SELECT m.*,
            CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS is_fav
            FROM movies m
            LEFT JOIN favorites f ON m.id = f.movie_id AND f.user_id = ?
            ORDER BY is_fav DESC, m.rating DESC''', (user_id,)).fetchall()

    fav_ids = []
    if 'user_id' in session:
        favs = conn.execute("SELECT movie_id FROM favorites WHERE user_id=?", (user_id,)).fetchall()
        fav_ids = [f['movie_id'] for f in favs]
    conn.close()
    return render_template('index.html', movies=movies, fav_ids=fav_ids, show_fav=show_fav)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
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
        password = hash_password(request.form['password'])
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/fav/<int:movie_id>')
def toggle_fav(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    existing = conn.execute("SELECT id FROM favorites WHERE user_id=? AND movie_id=?",
                            (session['user_id'], movie_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM favorites WHERE id=?", (existing['id'],))
    else:
        conn.execute("INSERT INTO favorites (user_id, movie_id) VALUES (?, ?)",
                     (session['user_id'], movie_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


init_db()

if __name__ == '__main__':
    app.run(debug=True)
