-- Этап 2 «Библиотека» — SQLite/Letos
-- ВАЖНО: SQLite не поддерживает хранимые процедуры CREATE PROCEDURE.
-- Поэтому ниже оформлены эквиваленты процедур как именованные
-- параметризованные SQL-операции, которые вызываются из Python.
-- Для преподавателя, требующего именно CREATE PROCEDURE/EXEC,
-- необходим SQL Server-вариант из предыдущего пакета.

-- 1. proc_authors_GetAll
SELECT author_id, full_name FROM authors ORDER BY full_name;

-- 2. proc_books_GetAll
SELECT * FROM v_book_catalog ORDER BY title;

-- 3. proc_books_GetById :book_id
SELECT * FROM v_book_catalog WHERE book_id = :book_id;

-- 4. proc_books_Search :query
SELECT * FROM v_book_catalog
WHERE title LIKE '%' || :query || '%'
   OR author LIKE '%' || :query || '%'
ORDER BY title;

-- 5. proc_readers_GetAll
SELECT reader_id, full_name, phone, email, registered_on
FROM readers ORDER BY full_name;

-- 6. proc_loans_GetByReader :reader_id
SELECT * FROM v_reader_loans
WHERE loan_id IN (SELECT loan_id FROM loans WHERE reader_id=:reader_id)
ORDER BY loan_date DESC;

-- 7. proc_readers_Create
-- Параметры: :full_name, :phone, :email, :registered_on
INSERT INTO readers(full_name, phone, email, registered_on)
VALUES (:full_name, :phone, :email, :registered_on);

-- 8. proc_readers_Update
-- Параметры: :reader_id, :full_name, :phone, :email
UPDATE readers
SET full_name=:full_name, phone=:phone, email=:email
WHERE reader_id=:reader_id;

-- 9. proc_readers_Delete
-- Параметр: :reader_id
DELETE FROM readers WHERE reader_id=:reader_id;

-- 10. proc_readers_CountLoans
-- Параметр: :reader_id
SELECT COUNT(*) AS loan_count FROM loans WHERE reader_id=:reader_id;

-- 11. proc_books_CountCopies
-- Параметр: :book_id
SELECT total_copies FROM books WHERE book_id=:book_id;

-- 12. proc_report_Overdue
SELECT * FROM v_overdue_loans ORDER BY due_date;

-- 13. proc_report_PopularBooks
SELECT b.book_id, b.title, COUNT(li.loan_item_id) AS issue_count
FROM books b
LEFT JOIN loan_items li ON li.book_id=b.book_id
GROUP BY b.book_id, b.title
ORDER BY issue_count DESC, b.title;

-- 14. proc_report_ReaderActivity
SELECT r.reader_id, r.full_name, COUNT(l.loan_id) AS loan_count
FROM readers r
LEFT JOIN loans l ON l.reader_id=r.reader_id
GROUP BY r.reader_id, r.full_name
ORDER BY loan_count DESC, r.full_name;

-- 15. Транзакционная операция выдачи книги
-- Выполняется из Python: BEGIN; INSERT loans; INSERT loan_items; COMMIT.
-- При ошибке: ROLLBACK.

-- 16. Транзакционная операция возврата книги
-- Выполняется из Python: BEGIN; UPDATE loan_items; UPDATE loans; COMMIT.
-- При ошибке: ROLLBACK.
