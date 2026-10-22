-- Тестирование эквивалентов процедур в SQLite/Letos

-- SELECT
SELECT * FROM v_book_catalog;
SELECT * FROM v_book_catalog WHERE book_id=1;
SELECT * FROM v_book_catalog WHERE title LIKE '%мир%';
SELECT * FROM readers;
SELECT * FROM v_reader_loans WHERE loan_id IN
  (SELECT loan_id FROM loans WHERE reader_id=1);

-- OUTPUT-аналог: последняя вставленная запись
INSERT INTO readers(full_name,phone,email,registered_on)
VALUES ('Тестовый Читатель','+79991112233','test_reader@example.ru','2026-10-19');
SELECT last_insert_rowid() AS new_reader_id;

-- UPDATE
UPDATE readers SET full_name='Тестовый Читатель Обновлённый'
WHERE phone='+79991112233';

-- COUNT
SELECT COUNT(*) AS loan_count FROM loans WHERE reader_id=1;

-- DELETE
DELETE FROM readers WHERE phone='+79991112233';

-- Отчёты
SELECT * FROM v_overdue_loans;
SELECT b.title, COUNT(li.loan_item_id) AS issue_count
FROM books b LEFT JOIN loan_items li ON li.book_id=b.book_id
GROUP BY b.book_id ORDER BY issue_count DESC;

-- Негативные тесты:
-- 1) внешний ключ:
-- INSERT INTO loans(reader_id,employee_id,loan_date,due_date,status)
-- VALUES (999,1,'2026-10-19','2026-11-02','выдана');
-- ожидается ошибка FOREIGN KEY constraint failed.
--
-- 2) уникальность:
-- INSERT INTO readers(full_name,phone,email,registered_on)
-- VALUES ('Дубликат','+79990000001','dup@example.ru','2026-10-19');
-- ожидается ошибка UNIQUE constraint failed.
