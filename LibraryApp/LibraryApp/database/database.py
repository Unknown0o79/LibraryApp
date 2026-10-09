import sqlite3
from datetime import date


class Database:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row

        # Включаем поддержку внешних ключей
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.create_tables()
        self.add_demo_data()

    # =========================================================
    # СОЗДАНИЕ ТАБЛИЦ
    # =========================================================

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                genre TEXT,
                year INTEGER,
                publisher TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                available INTEGER NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                registration_date TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'Выдана',

                FOREIGN KEY (book_id)
                    REFERENCES books(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (reader_id)
                    REFERENCES readers(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()

    # =========================================================
    # ДЕМО-ДАННЫЕ
    # =========================================================

    def add_demo_data(self):
        cursor = self.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")
        books_count = cursor.fetchone()[0]

        if books_count == 0:
            books = [
                (
                    "Преступление и наказание",
                    "Ф. М. Достоевский",
                    "9785170906996",
                    "Роман",
                    1866,
                    "АСТ",
                    3,
                    3
                ),
                (
                    "Война и мир",
                    "Л. Н. Толстой",
                    "9785171187868",
                    "Роман",
                    1869,
                    "АСТ",
                    2,
                    2
                ),
                (
                    "Мастер и Маргарита",
                    "М. А. Булгаков",
                    "9785170873241",
                    "Роман",
                    1967,
                    "АСТ",
                    4,
                    4
                ),
                (
                    "1984",
                    "Джордж Оруэлл",
                    "9780451524935",
                    "Антиутопия",
                    1949,
                    "Signet Classic",
                    2,
                    2
                )
            ]

            cursor.executemany("""
                INSERT INTO books
                (
                    title,
                    author,
                    isbn,
                    genre,
                    year,
                    publisher,
                    quantity,
                    available
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, books)
        cursor.execute("SELECT COUNT(*) FROM readers")
        readers_count = cursor.fetchone()[0]

        if readers_count == 0:
            readers = [
                (
                    "Иванов Иван Иванович",
                    "+7 900 111-22-33",
                    "ivanov@example.com",
                    str(date.today())
                ),
                (
                    "Петров Петр Петрович",
                    "+7 900 444-55-66",
                    "petrov@example.com",
                    str(date.today())
                )
            ]

            cursor.executemany("""
                INSERT INTO readers
                (
                    full_name,
                    phone,
                    email,
                    registration_date
                )
                VALUES (?, ?, ?, ?)
            """, readers)

        self.connection.commit()

    # =========================================================
    # ЗАКРЫТИЕ БАЗЫ
    # =========================================================

    def close(self):
        self.connection.close()