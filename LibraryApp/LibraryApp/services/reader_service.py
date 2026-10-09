from datetime import date


class ReaderService:
    def __init__(self, database):
        self.database = database

    def get_readers(self, search=""):
        cursor = self.database.connection.cursor()

        if search:
            value = f"%{search}%"

            cursor.execute("""
                SELECT *
                FROM readers
                WHERE full_name LIKE ?
                   OR phone LIKE ?
                   OR email LIKE ?
                ORDER BY full_name
            """, (value, value, value))
        else:
            cursor.execute("""
                SELECT *
                FROM readers
                ORDER BY full_name
            """)

        return cursor.fetchall()

    def add_reader(self, full_name, phone, email):
        full_name = full_name.strip() if isinstance(full_name, str) else ""
        phone = phone.strip() if isinstance(phone, str) else ""
        email = email.strip() if isinstance(email, str) else ""
        if not full_name:
            raise ValueError("ФИО читателя обязательно.")

        cursor = self.database.connection.cursor()

        cursor.execute("""
            INSERT INTO readers
            (full_name, phone, email, registration_date)
            VALUES (?, ?, ?, ?)
        """, (
            full_name,
            phone,
            email,
            str(date.today())
        ))

        self.database.connection.commit()

    def update_reader(self, reader_id, full_name, phone, email):
        full_name = full_name.strip() if isinstance(full_name, str) else ""
        phone = phone.strip() if isinstance(phone, str) else ""
        email = email.strip() if isinstance(email, str) else ""
        if not full_name:
            raise ValueError("ФИО читателя обязательно.")

        cursor = self.database.connection.cursor()

        cursor.execute("""
            UPDATE readers
            SET full_name = ?,
                phone = ?,
                email = ?
            WHERE id = ?
        """, (
            full_name,
            phone,
            email,
            reader_id
        ))

        self.database.connection.commit()

    def delete_reader(self, reader_id):
        cursor = self.database.connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE reader_id = ?
              AND status = 'Выдана'
        """, (reader_id,))

        active_loans = cursor.fetchone()[0]

        if active_loans > 0:
            raise ValueError(
                "Нельзя удалить читателя, у которого есть "
                "выданные книги."
            )

        cursor.execute("""
            DELETE FROM loans
            WHERE reader_id = ?
        """, (reader_id,))

        cursor.execute("""
            DELETE FROM readers
            WHERE id = ?
        """, (reader_id,))

        self.database.connection.commit()