class BookService:

    def __init__(self, database):
        self.database = database

    # =========================================================
    # ПОЛУЧЕНИЕ КНИГ
    # =========================================================

    def get_books(self, search=""):
        cursor = self.database.connection.cursor()

        if search:
            value = f"%{search}%"

            cursor.execute("""
                SELECT *
                FROM books
                WHERE title LIKE ?
                   OR author LIKE ?
                   OR isbn LIKE ?
                   OR genre LIKE ?
                ORDER BY title
            """, (
                value,
                value,
                value,
                value
            ))
        else:
            cursor.execute("""
                SELECT *
                FROM books
                ORDER BY title
            """)

        return cursor.fetchall()

    # =========================================================
    # ДОБАВЛЕНИЕ
    # =========================================================

    def add_book(
        self,
        title,
        author,
        isbn,
        genre,
        year,
        publisher,
        quantity
    ):
        title = title.strip() if isinstance(title, str) else ""
        author = author.strip() if isinstance(author, str) else ""
        isbn = isbn.strip() if isinstance(isbn, str) else ""
        genre = genre.strip() if isinstance(genre, str) else ""
        publisher = publisher.strip() if isinstance(publisher, str) else ""


        if not title:
            raise ValueError("Название книги обязательно.")

        if not author:
            raise ValueError("Автор обязателен.")

        if quantity <= 0:
            raise ValueError(
                "Количество экземпляров должно быть больше нуля."
            )

        cursor = self.database.connection.cursor()

        cursor.execute("""
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
        """, (
            title,
            author,
            isbn or None,
            genre,
            year,
            publisher,
            quantity,
            quantity
        ))

        self.database.connection.commit()

    # =========================================================
    # ИЗМЕНЕНИЕ
    # =========================================================

    def update_book(
        self,
        book_id,
        title,
        author,
        isbn,
        genre,
        year,
        publisher,
        quantity
    ):
        title = title.strip() if isinstance(title, str) else ""
        author = author.strip() if isinstance(author, str) else ""
        isbn = isbn.strip() if isinstance(isbn, str) else ""
        genre = genre.strip() if isinstance(genre, str) else ""
        publisher = publisher.strip() if isinstance(publisher, str) else ""

        if not title:
            raise ValueError("Название книги обязательно.")

        if not author:
            raise ValueError("Автор обязателен.")

        if quantity <= 0:
            raise ValueError(
                "Количество экземпляров должно быть больше нуля."
            )

        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT quantity, available
            FROM books
            WHERE id = ?
        """, (book_id,))

        old_book = cursor.fetchone()

        if old_book is None:
            raise ValueError("Книга не найдена.")

        # Считаем количество экземпляров,
        # которые сейчас находятся у читателей.
        issued = old_book["quantity"] - old_book["available"]

        if quantity < issued:
            raise ValueError(
                f"Нельзя установить количество меньше {issued}, "
                f"так как столько экземпляров сейчас выдано."
            )

        new_available = quantity - issued

        cursor.execute("""
            UPDATE books
            SET title = ?,
                author = ?,
                isbn = ?,
                genre = ?,
                year = ?,
                publisher = ?,
                quantity = ?,
                available = ?
            WHERE id = ?
        """, (
            title,
            author,
            isbn or None,
            genre,
            year,
            publisher,
            quantity,
            new_available,
            book_id
        ))
        self.database.connection.commit()

    # =========================================================
    # УДАЛЕНИЕ
    # =========================================================

    def delete_book(self, book_id):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE book_id = ?
              AND status = 'Выдана'
        """, (book_id,))

        active_loans = cursor.fetchone()[0]

        if active_loans > 0:
            raise ValueError(
                "Нельзя удалить книгу, которая сейчас находится "
                "у читателя."
            )

        cursor.execute("""
            DELETE FROM loans
            WHERE book_id = ?
        """, (book_id,))

        cursor.execute("""
            DELETE FROM books
            WHERE id = ?
        """, (book_id,))

        self.database.connection.commit()

    # =========================================================
    # ДОСТУПНЫЕ КНИГИ
    # =========================================================

    def get_available_books(self):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM books
            WHERE available > 0
            ORDER BY title
        """)

        return cursor.fetchall()