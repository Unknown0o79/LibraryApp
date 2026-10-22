ЭТАП 2 — БИБЛИОТЕКА — LETOS / SQLITE

1. Открой Letos.
2. Выбери Open Database / Открыть базу данных.
3. Открой файл LibraryDB.db из этого архива.
4. Открой SQL Editor / редактор SQL.
5. Для просмотра каталога выполни:
   SELECT * FROM v_book_catalog;
6. Для просмотра просроченных:
   SELECT * FROM v_overdue_loans;
7. Для популярных книг:
   SELECT b.title, COUNT(li.loan_item_id) AS issue_count
   FROM books b LEFT JOIN loan_items li ON li.book_id=b.book_id
   GROUP BY b.book_id ORDER BY issue_count DESC;

Python:
1. Установи Python 3.
2. В той же папке находится biblioteka_letos.py.
3. Запусти:
   python biblioteka_letos.py

ВАЖНО:
SQLite/Letos НЕ поддерживает хранимые процедуры CREATE PROCEDURE/EXEC.
Поэтому 03_Library_procedures_sqlite.sql содержит параметризованные
SQL-эквиваленты процедур, а транзакции реализованы в Python через
BEGIN/COMMIT/ROLLBACK. Если преподаватель требует именно T-SQL
CREATE PROCEDURE, нужен SQL Server-вариант.
