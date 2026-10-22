-- Тестирование триггеров
INSERT INTO readers(full_name,phone,email,registered_on) VALUES('Тест Триггеров','+79998887766','trigger_test@example.ru',date('now'));
SELECT * FROM audit_changes WHERE table_name='readers' AND operation='INSERT' ORDER BY audit_id DESC LIMIT 1;
UPDATE readers SET phone='+79998887767' WHERE email='trigger_test@example.ru';
SELECT * FROM audit_changes WHERE table_name='readers' AND operation='UPDATE' ORDER BY audit_id DESC LIMIT 1;
DELETE FROM readers WHERE email='trigger_test@example.ru';
SELECT * FROM audit_changes WHERE table_name='readers' AND operation='DELETE' ORDER BY audit_id DESC LIMIT 1;
DELETE FROM v_active_books WHERE book_id=10;
SELECT book_id,title,is_archived FROM books WHERE book_id=10;
UPDATE books SET total_copies=total_copies WHERE book_id IN(1,2,3);
SELECT * FROM audit_changes ORDER BY audit_id DESC;
-- При выдаче сверх total_copies триггер выдаёт: Нельзя выдать книгу: все экземпляры уже выданы
