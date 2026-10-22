import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'LibraryDB.db'

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    publish_year INTEGER,
    total_copies INTEGER NOT NULL DEFAULT 1 CHECK(total_copies >= 0),
    FOREIGN KEY(author_id) REFERENCES authors(author_id),
    FOREIGN KEY(genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE IF NOT EXISTS readers (
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    loan_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    FOREIGN KEY(reader_id) REFERENCES readers(reader_id),
    FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS loan_items (
    loan_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
    FOREIGN KEY(loan_id) REFERENCES loans(loan_id),
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);
"""

SEED = """
INSERT OR IGNORE INTO authors(full_name) VALUES
('Лев Толстой'), ('Фёдор Достоевский'), ('Михаил Булгаков'),
('Александр Пушкин'), ('Джордж Оруэлл');

INSERT OR IGNORE INTO genres(name) VALUES
('Роман'), ('Классика'), ('Фантастика');

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT 'Война и мир', a.author_id, g.genre_id, 1869, 4
FROM authors a, genres g WHERE a.full_name='Лев Толстой' AND g.name='Роман';

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT 'Преступление и наказание', a.author_id, g.genre_id, 1866, 3
FROM authors a, genres g WHERE a.full_name='Фёдор Достоевский' AND g.name='Роман';

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT 'Мастер и Маргарита', a.author_id, g.genre_id, 1967, 2
FROM authors a, genres g WHERE a.full_name='Михаил Булгаков' AND g.name='Классика';

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT 'Евгений Онегин', a.author_id, g.genre_id, 1833, 2
FROM authors a, genres g WHERE a.full_name='Александр Пушкин' AND g.name='Классика';

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT '1984', a.author_id, g.genre_id, 1949, 1
FROM authors a, genres g WHERE a.full_name='Джордж Оруэлл' AND g.name='Фантастика';

INSERT OR IGNORE INTO books(title, author_id, genre_id, publish_year, total_copies)
SELECT 'Анна Каренина', a.author_id, g.genre_id, 1878, 2
FROM authors a, genres g WHERE a.full_name='Лев Толстой' AND g.name='Роман';

INSERT OR IGNORE INTO readers(full_name, phone) VALUES
('Иванов Иван Иванович', '+7 900 111-22-33'),
('Петрова Анна Сергеевна', '+7 900 222-33-44'),
('Сидоров Максим Олегович', '+7 900 333-44-55');

INSERT OR IGNORE INTO employees(full_name, position) VALUES
('Кузнецова Мария Викторовна', 'Библиотекарь'),
('Смирнов Алексей Павлович', 'Администратор');

INSERT OR IGNORE INTO loans(reader_id, employee_id, loan_date, due_date, return_date)
SELECT r.reader_id, e.employee_id, '2026-10-10', '2026-10-24', NULL
FROM readers r, employees e
WHERE r.full_name='Иванов Иван Иванович' AND e.full_name='Кузнецова Мария Викторовна'
AND NOT EXISTS (SELECT 1 FROM loans WHERE loan_date='2026-10-10' AND reader_id=r.reader_id);

INSERT OR IGNORE INTO loans(reader_id, employee_id, loan_date, due_date, return_date)
SELECT r.reader_id, e.employee_id, '2026-10-12', '2026-10-26', NULL
FROM readers r, employees e
WHERE r.full_name='Петрова Анна Сергеевна' AND e.full_name='Кузнецова Мария Викторовна'
AND NOT EXISTS (SELECT 1 FROM loans WHERE loan_date='2026-10-12' AND reader_id=r.reader_id);

INSERT OR IGNORE INTO loan_items(loan_id, book_id, quantity)
SELECT l.loan_id, b.book_id, 1 FROM loans l, books b
WHERE l.loan_date='2026-10-10' AND b.title='Война и мир'
AND NOT EXISTS (SELECT 1 FROM loan_items x WHERE x.loan_id=l.loan_id AND x.book_id=b.book_id);

INSERT OR IGNORE INTO loan_items(loan_id, book_id, quantity)
SELECT l.loan_id, b.book_id, 1 FROM loans l, books b
WHERE l.loan_date='2026-10-12' AND b.title='1984'
AND NOT EXISTS (SELECT 1 FROM loan_items x WHERE x.loan_id=l.loan_id AND x.book_id=b.book_id);
"""


def init_database():
    # Учебное приложение должно запускаться каждый раз на чистых тестовых данных.
    # Удаляем старую БД, чтобы накопившиеся выдачи не ломали тесты.
    if DB_PATH.exists():
        DB_PATH.unlink()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    connection.executescript(SCHEMA)
    connection.executescript(SEED)
    connection.commit()
    return connection
