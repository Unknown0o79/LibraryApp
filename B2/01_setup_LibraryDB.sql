-- Этап 2. Библиотека. SQLite / Letos
-- Этот файл создаёт структуру БД, индексы, представления и тестовые данные.
-- Запускать в пустой базе SQLite через Letos.

PRAGMA foreign_keys = ON;

-- Таблицы

CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE
);
CREATE TABLE genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    publish_year INTEGER,
    isbn TEXT UNIQUE,
    total_copies INTEGER NOT NULL DEFAULT 1 CHECK(total_copies >= 0),
    FOREIGN KEY(author_id) REFERENCES authors(author_id),
    FOREIGN KEY(genre_id) REFERENCES genres(genre_id)
);
CREATE TABLE readers (
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT UNIQUE,
    registered_on TEXT NOT NULL
);
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL
);
CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    loan_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'выдана',
    FOREIGN KEY(reader_id) REFERENCES readers(reader_id),
    FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
);
CREATE TABLE loan_items (
    loan_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    returned_on TEXT,
    FOREIGN KEY(loan_id) REFERENCES loans(loan_id) ON DELETE CASCADE,
    FOREIGN KEY(book_id) REFERENCES books(book_id)
);

CREATE INDEX ix_books_title ON books(title);
CREATE INDEX ix_books_author ON books(author_id);
CREATE INDEX ix_loans_date ON loans(loan_date);
CREATE INDEX ix_loans_status ON loans(status);
CREATE INDEX ix_loans_reader ON loans(reader_id);

CREATE VIEW v_book_catalog AS
SELECT b.book_id, b.title, a.full_name AS author, g.name AS genre,
       b.publish_year, b.isbn, b.total_copies
FROM books b
JOIN authors a ON a.author_id=b.author_id
JOIN genres g ON g.genre_id=b.genre_id;

CREATE VIEW v_reader_loans AS
SELECT l.loan_id, r.full_name AS reader, b.title AS book,
       l.loan_date, l.due_date, l.status, li.returned_on
FROM loans l
JOIN readers r ON r.reader_id=l.reader_id
JOIN loan_items li ON li.loan_id=l.loan_id
JOIN books b ON b.book_id=li.book_id;

CREATE VIEW v_overdue_loans AS
SELECT l.loan_id, r.full_name AS reader, b.title AS book,
       l.loan_date, l.due_date
FROM loans l
JOIN readers r ON r.reader_id=l.reader_id
JOIN loan_items li ON li.loan_id=l.loan_id
JOIN books b ON b.book_id=li.book_id
WHERE l.status='выдана' AND date(l.due_date) < date('now');


-- Заполнение данными выполняется отдельным файлом seed_LibraryDB.sql.
