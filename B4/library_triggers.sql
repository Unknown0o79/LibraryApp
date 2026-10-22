-- Этап 4. Библиотека — SQLite / Letos
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS audit_changes (audit_id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT NOT NULL, operation TEXT NOT NULL CHECK(operation IN ('INSERT','UPDATE','DELETE')), row_id INTEGER, old_data TEXT, new_data TEXT, actor TEXT NOT NULL DEFAULT 'SQLite/Letos', changed_at TEXT NOT NULL DEFAULT(datetime('now','localtime')));

CREATE TRIGGER IF NOT EXISTS trg_books_audit_insert AFTER INSERT ON books BEGIN INSERT INTO audit_changes(table_name,operation,row_id,new_data) VALUES('books','INSERT',NEW.book_id,'title='||NEW.title||'; copies='||NEW.total_copies); END;
CREATE TRIGGER IF NOT EXISTS trg_books_audit_update AFTER UPDATE ON books BEGIN INSERT INTO audit_changes(table_name,operation,row_id,old_data,new_data) VALUES('books','UPDATE',NEW.book_id,'title='||OLD.title||'; copies='||OLD.total_copies||'; archived='||OLD.is_archived,'title='||NEW.title||'; copies='||NEW.total_copies||'; archived='||NEW.is_archived); END;
CREATE TRIGGER IF NOT EXISTS trg_books_audit_delete AFTER DELETE ON books BEGIN INSERT INTO audit_changes(table_name,operation,row_id,old_data) VALUES('books','DELETE',OLD.book_id,'title='||OLD.title||'; copies='||OLD.total_copies); END;

CREATE TRIGGER IF NOT EXISTS trg_readers_audit_insert AFTER INSERT ON readers BEGIN INSERT INTO audit_changes(table_name,operation,row_id,new_data) VALUES('readers','INSERT',NEW.reader_id,'full_name='||NEW.full_name||'; phone='||COALESCE(NEW.phone,'')); END;
CREATE TRIGGER IF NOT EXISTS trg_readers_audit_update AFTER UPDATE ON readers BEGIN INSERT INTO audit_changes(table_name,operation,row_id,old_data,new_data) VALUES('readers','UPDATE',NEW.reader_id,'full_name='||OLD.full_name||'; phone='||COALESCE(OLD.phone,''),'full_name='||NEW.full_name||'; phone='||COALESCE(NEW.phone,'')); END;
CREATE TRIGGER IF NOT EXISTS trg_readers_audit_delete AFTER DELETE ON readers BEGIN INSERT INTO audit_changes(table_name,operation,row_id,old_data) VALUES('readers','DELETE',OLD.reader_id,'full_name='||OLD.full_name||'; phone='||COALESCE(OLD.phone,'')); END;

CREATE TRIGGER IF NOT EXISTS trg_loan_items_check_copies BEFORE INSERT ON loan_items WHEN (SELECT COUNT(*) FROM loan_items li JOIN loans l ON l.loan_id=li.loan_id WHERE li.book_id=NEW.book_id AND li.returned_on IS NULL AND l.status='выдана') >= (SELECT total_copies FROM books WHERE book_id=NEW.book_id) BEGIN SELECT RAISE(ABORT,'Нельзя выдать книгу: все экземпляры уже выданы'); END;

ALTER TABLE books ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0;
CREATE VIEW IF NOT EXISTS v_active_books AS SELECT book_id,title,author_id,genre_id,publish_year,isbn,total_copies FROM books WHERE is_archived=0;
CREATE TRIGGER IF NOT EXISTS trg_active_books_instead_delete INSTEAD OF DELETE ON v_active_books BEGIN UPDATE books SET is_archived=1 WHERE book_id=OLD.book_id; END;
