import sqlite3
import pytest
from database.database import Database
from services.book_service import BookService
from services.reader_service import ReaderService
from services.loan_service import LoanService

@pytest.fixture()
def db(tmp_path):
    database = Database(str(tmp_path / 'test_library.db'))
    yield database
    database.close()

def test_01_fresh_database_has_demo_books_and_readers(db):
    assert db.connection.execute('SELECT COUNT(*) FROM books').fetchone()[0] == 4
    assert db.connection.execute('SELECT COUNT(*) FROM readers').fetchone()[0] == 2

def test_02_reopen_does_not_duplicate_demo_data(tmp_path):
    path = tmp_path / 'library.db'
    Database(str(path)).close()
    db = Database(str(path))
    assert db.connection.execute('SELECT COUNT(*) FROM books').fetchone()[0] == 4
    assert db.connection.execute('SELECT COUNT(*) FROM readers').fetchone()[0] == 2
    db.close()

def test_03_add_book(db):
    s=BookService(db); s.add_book('Тестовая книга','Тестовый автор','9999999999999','Тест',2026,'Тест',2)
    b=s.get_books('Тестовая книга')[0]
    assert b['quantity']==2 and b['available']==2

def test_04_add_book_requires_title(db):
    with pytest.raises(ValueError, match='Название книги обязательно'):
        BookService(db).add_book('','Автор','123','','', '',1)

def test_05_add_book_requires_author(db):
    with pytest.raises(ValueError, match='Автор обязателен'):
        BookService(db).add_book('Книга','','123','','','',1)

def test_06_quantity_must_be_positive(db):
    with pytest.raises(ValueError, match='больше нуля'):
        BookService(db).add_book('Книга','Автор','123','','','',0)

def test_07_duplicate_isbn_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        BookService(db).add_book('Дубликат','Автор','9785170906996','','','',1)

def test_08_search_by_author(db):
    result=BookService(db).get_books('Достоевский')
    assert len(result)==1

def test_09_update_book_preserves_issued_copy(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db)
    b=bs.get_books()[0]; r=rs.get_readers()[0]
    ls.create_loan(b['id'],r['id'],14)
    bs.update_book(b['id'],b['title'],b['author'],b['isbn'],b['genre'],b['year'],b['publisher'],5)
    u=bs.get_books()[0]
    assert u['quantity']==5 and u['available']==4

def test_10_update_book_cannot_go_below_issued(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db)
    b=bs.get_books()[0]; r=rs.get_readers()[0]
    ls.create_loan(b['id'],r['id'],14); ls.create_loan(b['id'],r['id'],14)
    with pytest.raises(ValueError, match='Нельзя установить количество'):
        bs.update_book(b['id'],b['title'],b['author'],b['isbn'],b['genre'],b['year'],b['publisher'],1)

def test_11_update_book_requires_title(db):
    b=BookService(db).get_books()[0]
    with pytest.raises(ValueError, match='Название книги обязательно'):
        BookService(db).update_book(b['id'],'',b['author'],b['isbn'],b['genre'],b['year'],b['publisher'],b['quantity'])

def test_12_update_book_requires_author(db):
    b=BookService(db).get_books()[0]
    with pytest.raises(ValueError, match='Автор обязателен'):
        BookService(db).update_book(b['id'],b['title'],'',b['isbn'],b['genre'],b['year'],b['publisher'],b['quantity'])

def test_13_update_book_quantity_positive(db):
    b=BookService(db).get_books()[0]
    with pytest.raises(ValueError, match='больше нуля'):
        BookService(db).update_book(b['id'],b['title'],b['author'],b['isbn'],b['genre'],b['year'],b['publisher'],0)

def test_14_update_unknown_book(db):
    with pytest.raises(ValueError, match='Книга не найдена'):
        BookService(db).update_book(99999,'Книга','Автор',None,'',None,'',1)

def test_15_delete_book(db):
    s=BookService(db); b=s.get_books()[0]; s.delete_book(b['id'])
    assert all(x['id']!=b['id'] for x in s.get_books())

def test_16_add_reader_and_search(db):
    s=ReaderService(db); s.add_reader('Сидоров Сидор Сидорович','+7 900 000-00-00','sidorov@example.com')
    r=s.get_readers('Сидоров')[0]
    assert r['email']=='sidorov@example.com'

def test_17_reader_requires_name(db):
    with pytest.raises(ValueError, match='ФИО читателя обязательно'):
        ReaderService(db).add_reader('','','')

def test_18_update_reader(db):
    s=ReaderService(db); r=s.get_readers()[0]
    s.update_reader(r['id'],'Обновлённый Читатель','+7 900 111-11-11','updated@example.com')
    assert s.get_readers('Обновлённый')[0]['email']=='updated@example.com'

def test_19_update_reader_requires_name(db):
    r=ReaderService(db).get_readers()[0]
    with pytest.raises(ValueError, match='ФИО читателя обязательно'):
        ReaderService(db).update_reader(r['id'],'','','')

def test_20_delete_reader(db):
    s=ReaderService(db); r=s.get_readers()[0]; s.delete_reader(r['id'])
    assert all(x['id']!=r['id'] for x in s.get_readers())

def test_21_create_loan_reduces_available(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db)
    b=bs.get_books()[0]; r=rs.get_readers()[0]; ls.create_loan(b['id'],r['id'],14)
    assert bs.get_books()[0]['available']==b['available']-1

def test_22_loan_zero_days_rejected(db):
    b=BookService(db).get_books()[0]; r=ReaderService(db).get_readers()[0]
    with pytest.raises(ValueError, match='больше нуля'):
        LoanService(db).create_loan(b['id'],r['id'],0)

def test_23_unknown_book_rejected(db):
    r=ReaderService(db).get_readers()[0]
    with pytest.raises(ValueError, match='Книга не найдена'):
        LoanService(db).create_loan(99999,r['id'],14)

def test_24_unknown_reader_rejected(db):
    b=BookService(db).get_books()[0]
    with pytest.raises(ValueError, match='Читатель не найден'):
        LoanService(db).create_loan(b['id'],99999,14)

def test_25_unavailable_book_rejected(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db)
    b=bs.get_books()[0]; r=rs.get_readers()[0]
    for _ in range(b['quantity']): ls.create_loan(b['id'],r['id'],14)
    with pytest.raises(ValueError, match='Нет доступных экземпляров'):
        ls.create_loan(b['id'],r['id'],14)

def test_26_return_restores_stock_and_closes_loan(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db)
    b=bs.get_books()[0]; r=rs.get_readers()[0]; ls.create_loan(b['id'],r['id'],14)
    loan_id=ls.get_active_loans()[0]['id']; ls.return_book(loan_id)
    assert bs.get_books()[0]['available']==b['available']
    assert ls.get_active_loans()==[]
    assert ls.get_loan_history()[0]['status']=='Возвращена'

def test_27_double_return_rejected(db):
    b=BookService(db).get_books()[0]; r=ReaderService(db).get_readers()[0]; ls=LoanService(db)
    ls.create_loan(b['id'],r['id'],14); loan_id=ls.get_active_loans()[0]['id']; ls.return_book(loan_id)
    with pytest.raises(ValueError, match='Активная выдача не найдена'):
        ls.return_book(loan_id)

def test_28_cannot_delete_book_with_active_loan(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db); b=bs.get_books()[0]; r=rs.get_readers()[0]
    ls.create_loan(b['id'],r['id'],14)
    with pytest.raises(ValueError, match='Нельзя удалить книгу'):
        bs.delete_book(b['id'])

def test_29_cannot_delete_reader_with_active_loan(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db); b=bs.get_books()[0]; r=rs.get_readers()[0]
    ls.create_loan(b['id'],r['id'],14)
    with pytest.raises(ValueError, match='Нельзя удалить читателя'):
        rs.delete_reader(r['id'])

def test_30_available_books_excludes_fully_issued_book(db):
    bs=BookService(db); rs=ReaderService(db); ls=LoanService(db); b=bs.get_books()[0]; r=rs.get_readers()[0]
    for _ in range(b['quantity']): ls.create_loan(b['id'],r['id'],14)
    assert b['id'] not in {x['id'] for x in bs.get_available_books()}

def test_31_new_loan_is_not_overdue(db):
    b=BookService(db).get_books()[0]; r=ReaderService(db).get_readers()[0]; ls=LoanService(db)
    ls.create_loan(b['id'],r['id'],14)
    assert ls.get_overdue_count()==0


def test_32_add_book_rejects_whitespace_title(db):
    with pytest.raises(ValueError, match='Название книги обязательно'):
        BookService(db).add_book('   ', 'Автор', '123456', '', None, '', 1)

def test_33_add_reader_rejects_whitespace_name(db):
    with pytest.raises(ValueError, match='ФИО читателя обязательно'):
        ReaderService(db).add_reader('   ', '', '')
