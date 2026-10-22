from datetime import date


def fn_loan_days(loan_date, due_date):
    """Скалярная функция: количество дней между датами выдачи и возврата."""
    if not loan_date or not due_date:
        return None
    start = date.fromisoformat(loan_date)
    end = date.fromisoformat(due_date)
    return (end - start).days


def fn_book_available_copies(connection, book_id):
    """Скалярная функция: количество доступных экземпляров книги."""
    row = connection.execute(
        """
        SELECT b.total_copies - COALESCE((
            SELECT SUM(li.quantity)
            FROM loan_items li
            JOIN loans l ON l.loan_id = li.loan_id
            WHERE li.book_id = b.book_id AND l.return_date IS NULL
        ), 0) AS available
        FROM books b WHERE b.book_id = ?
        """, (book_id,)
    ).fetchone()
    return int(row['available']) if row else None


def fn_book_search(connection, text):
    """Inline table-valued аналог: поиск книг по названию или автору."""
    pattern = f"%{(text or '').strip()}%"
    return connection.execute(
        """
        SELECT b.book_id, b.title, a.full_name AS author,
               g.name AS genre, b.publish_year, b.total_copies
        FROM books b
        JOIN authors a ON a.author_id = b.author_id
        JOIN genres g ON g.genre_id = b.genre_id
        WHERE b.title LIKE ? COLLATE NOCASE
           OR a.full_name LIKE ? COLLATE NOCASE
        ORDER BY b.title
        """, (pattern, pattern)
    ).fetchall()


def fn_reader_loans(connection, reader_id, date_from=None, date_to=None):
    """Inline table-valued аналог: выдачи выбранного читателя за период."""
    date_from = date_from or '1900-01-01'
    date_to = date_to or '2999-12-31'
    return connection.execute(
        """
        SELECT l.loan_id, r.full_name AS reader, b.title,
               l.loan_date, l.due_date, l.return_date
        FROM loans l
        JOIN readers r ON r.reader_id = l.reader_id
        JOIN loan_items li ON li.loan_id = l.loan_id
        JOIN books b ON b.book_id = li.book_id
        WHERE l.reader_id = ? AND l.loan_date BETWEEN ? AND ?
        ORDER BY l.loan_date DESC
        """, (reader_id, date_from, date_to)
    ).fetchall()


def fn_book_availability_report(connection):
    """Многооператорный табличный аналог: формирует отчёт доступности книг."""
    rows = connection.execute(
        """
        SELECT b.book_id, b.title, a.full_name AS author, b.total_copies,
               COALESCE((SELECT SUM(li.quantity) FROM loan_items li
                         JOIN loans l ON l.loan_id=li.loan_id
                         WHERE li.book_id=b.book_id AND l.return_date IS NULL), 0) AS issued
        FROM books b JOIN authors a ON a.author_id=b.author_id
        ORDER BY b.title
        """
    ).fetchall()
    report = []
    for row in rows:
        available = row['total_copies'] - row['issued']
        if available <= 0:
            status = 'нет экземпляров'
        elif available == 1:
            status = 'заканчивается'
        else:
            status = 'доступна'
        report.append({
            'book_id': row['book_id'],
            'title': row['title'],
            'author': row['author'],
            'total_copies': row['total_copies'],
            'issued': row['issued'],
            'available': available,
            'status': status,
        })
    return report


def register_sql_functions(connection):
    """Регистрирует скалярные функции, чтобы демонстрировать их в SELECT/WHERE."""
    connection.create_function('fn_LoanDays', 2, fn_loan_days)
    connection.create_function(
        'fn_BookAvailableCopies', 1,
        lambda book_id: fn_book_available_copies(connection, book_id)
    )
