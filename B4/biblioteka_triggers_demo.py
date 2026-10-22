import sqlite3
from pathlib import Path
DB=Path(__file__).with_name('LibraryDB.db')
with sqlite3.connect(DB) as con:
    con.execute("UPDATE books SET total_copies=total_copies+1 WHERE book_id=1")
    print('AFTER UPDATE:', con.execute("SELECT * FROM audit_changes ORDER BY audit_id DESC LIMIT 1").fetchone())
    con.execute("DELETE FROM v_active_books WHERE book_id=10")
    print('INSTEAD OF DELETE:', con.execute("SELECT book_id,title,is_archived FROM books WHERE book_id=10").fetchone())
    print('AUDIT:')
    for row in con.execute("SELECT audit_id,table_name,operation,row_id,changed_at FROM audit_changes ORDER BY audit_id DESC LIMIT 10"):
        print(row)
