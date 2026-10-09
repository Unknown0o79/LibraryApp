from datetime import date, timedelta


class LoanService:

    def __init__(self, database):
        self.database = database

    # =========================================================
    # ВЫДАЧА КНИГИ
    # =========================================================

    def create_loan(
        self,
        book_id,
        reader_id,
        days=14
    ):
        if days <= 0:
            raise ValueError(
                "Срок выдачи должен быть больше нуля."
            )

        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT available
            FROM books
            WHERE id = ?
        """, (book_id,))

        book = cursor.fetchone()

        if book is None:
            raise ValueError("Книга не найдена.")

        if book["available"] <= 0:
            raise ValueError(
                "Нет доступных экземпляров книги."
            )

        cursor.execute("""
            SELECT id
            FROM readers
            WHERE id = ?
        """, (reader_id,))

        reader = cursor.fetchone()

        if reader is None:
            raise ValueError("Читатель не найден.")

        issue_date = date.today()
        due_date = issue_date + timedelta(days=days)

        cursor.execute("""
            INSERT INTO loans
            (
                book_id,
                reader_id,
                issue_date,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, 'Выдана')
        """, (
            book_id,
            reader_id,
            str(issue_date),
            str(due_date)
        ))

        cursor.execute("""
            UPDATE books
            SET available = available - 1
            WHERE id = ?
        """, (book_id,))

        self.database.connection.commit()

    # =========================================================
    # ПОЛУЧЕНИЕ АКТИВНЫХ ВЫДАЧ
    # =========================================================

    def get_active_loans(self):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT
                loans.id,
                loans.book_id,
                loans.reader_id,
                books.title,
                readers.full_name,
                loans.issue_date,
                loans.due_date,
                loans.status,
                CASE
                    WHEN loans.due_date < ? THEN 'Просрочена'
                    ELSE loans.status
                END AS display_status
            FROM loans
            JOIN books
                ON books.id = loans.book_id
            JOIN readers
                ON readers.id = loans.reader_id
            WHERE loans.status = 'Выдана'
            ORDER BY loans.due_date
        """, (str(date.today()),))

        return cursor.fetchall()

    # =========================================================
    # ВОЗВРАТ
    # =========================================================

    def return_book(self, loan_id):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT book_id
            FROM loans
            WHERE id = ?
              AND status = 'Выдана'
        """, (loan_id,))

        loan = cursor.fetchone()

        if loan is None:
            raise ValueError(
                "Активная выдача не найдена."
            )

        cursor.execute("""
            UPDATE loans
            SET status = 'Возвращена',
                return_date = ?
            WHERE id = ?
        """, (
            str(date.today()),
            loan_id
        ))

        cursor.execute("""
            UPDATE books
            SET available = available + 1
            WHERE id = ?
        """, (loan["book_id"],))

        self.database.connection.commit()

    # =========================================================
    # ИСТОРИЯ ВЫДАЧ
    # =========================================================

    def get_loan_history(self):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT
                loans.id,
                books.title,
                readers.full_name,loans.issue_date,
                loans.due_date,
                loans.return_date,
                loans.status
            FROM loans
            JOIN books
                ON books.id = loans.book_id
            JOIN readers
                ON readers.id = loans.reader_id
            ORDER BY loans.issue_date DESC
        """)

        return cursor.fetchall()

    # =========================================================
    # ПРОСРОЧЕННЫЕ
    # =========================================================

    def get_overdue_count(self):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE status = 'Выдана'
              AND due_date < ?
        """, (str(date.today()),))

        return cursor.fetchone()[0]