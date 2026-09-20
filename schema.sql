-- Movie DB schema
-- Схема базы данных Movie DB
-- Проект: каталог фильмов с избранным
-- СУБД: SQLite

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица фильмов
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    year INTEGER NOT NULL,
    rating REAL DEFAULT 0,
    added_by INTEGER,
    FOREIGN KEY (added_by) REFERENCES users(id)
);

-- Таблица избранного (связь M:N между users и movies)
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    UNIQUE (user_id, movie_id)
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_movies_genre ON movies(genre);
CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(rating);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);

-- Представление: топ фильмов с количеством добавлений в избранное
CREATE VIEW IF NOT EXISTS top_movies AS
SELECT m.id, m.title, m.genre, m.rating, COUNT(f.id) AS favorites_count
FROM movies m
LEFT JOIN favorites f ON m.id = f.movie_id
GROUP BY m.id
ORDER BY m.rating DESC;
