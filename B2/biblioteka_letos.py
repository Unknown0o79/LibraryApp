import sqlite3
from pathlib import Path
from datetime import date, timedelta

DB_PATH = Path(__file__).with_name("LibraryDB.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def books_get_all(conn):
    return conn.execute("SELECT * FROM v_book_catalog ORDER BY title").fetchall()

def books_search(conn, query):
    return conn.execute("""
        SELECT * FROM v_book_catalog
        WHERE title LIKE ? OR author LIKE ?
        ORDER BY title
    """, (f"%{query}%", f"%{query}%")).fetchall()

def readers_get_all(conn):
    return conn.execute(
        "SELECT * FROM readers ORDER BY full_name"
    ).fetchall()

def reader_create(conn, full_name, phone, email):
    try:
        cur = conn.execute("""
            INSERT INTO readers(full_name, phone, email, registered_on)
            VALUES (?, ?, ?, ?)
        """, (full_name, phone, email, date.today().isoformat()))
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error:
        conn.rollback()
        raise

def issue_book(conn, reader_id, employee_id, book_id, days=14):
    """Транзакционный эквивалент proc_loans_Create."""
    try:
        book = conn.execute(
            "SELECT total_copies FROM books WHERE book_id=?", (book_id,)
        ).fetchone()
        if not book:
            raise ValueError("Книга не найдена")
        if book["total_copies"] <= 0:
            raise ValueError("Нет экземпляров книги")

        reader = conn.execute(
            "SELECT reader_id FROM readers WHERE reader_id=?", (reader_id,)
        ).fetchone()
        if not reader:
            raise ValueError("Читатель не найден")

        conn.execute("BEGIN")
        today = date.today()
        due = today + timedelta(days=days)
        cur = conn.execute("""
            INSERT INTO loans(reader_id, employee_id, loan_date, due_date, status)
            VALUES (?, ?, ?, ?, 'выдана')
        """, (reader_id, employee_id, today.isoformat(), due.isoformat()))
        loan_id = cur.lastrowid
        conn.execute("""
            INSERT INTO loan_items(loan_id, book_id, returned_on)
            VALUES (?, ?, NULL)
        """, (loan_id, book_id))
        conn.commit()
        return loan_id
    except Exception:
        conn.rollback()
        raise

def return_book(conn, loan_item_id):
    """Транзакционный эквивалент proc_loans_Return."""
    try:
        conn.execute("BEGIN")
        row = conn.execute("""
            SELECT loan_id FROM loan_items
            WHERE loan_item_id=? AND returned_on IS NULL
        """, (loan_item_id,)).fetchone()
        if not row:
            raise ValueError("Выдача не найдена или уже возвращена")
        conn.execute("""
            UPDATE loan_items SET returned_on=date('now')
            WHERE loan_item_id=?
        """, (loan_item_id,))
        conn.execute("""
            UPDATE loans SET status='возвращена'
            WHERE loan_id=?
        """, (row["loan_id"],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def report_overdue(conn):
    return conn.execute("SELECT * FROM v_overdue_loans ORDER BY due_date").fetchall()

def report_popular(conn):
    return conn.execute("""
        SELECT b.title, COUNT(li.loan_item_id) AS issue_count
        FROM books b
        LEFT JOIN loan_items li ON li.book_id=b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY issue_count DESC, b.title
    """).fetchall()

def main():
    with connect() as conn:
        print("=== КАТАЛОГ КНИГ ===")
        for row in books_get_all(conn):
            print(f'{row["book_id"]}. {row["title"]} — {row["author"]}')

        print("\n=== ПОИСК: \"война\" ===")
        for row in books_search(conn, "война"):
            print(f'{row["title"]} — {row["author"]}')

        print("\n=== ЧИТАТЕЛИ ===")
        for row in readers_get_all(conn)[:5]:
            print(f'{row["reader_id"]}. {row["full_name"]} — {row["phone"]}')

        print("\n=== ПРОСРОЧЕННЫЕ ВЫДАЧИ ===")
        for row in report_overdue(conn):
            print(f'{row["reader"]} — {row["book"]}, срок: {row["due_date"]}')

        print("\n=== ПОПУЛЯРНЫЕ КНИГИ ===")
        for row in report_popular(conn):
            print(f'{row["title"]} — {row["issue_count"]} выдач')

if __name__ == "__main__":
    main()
