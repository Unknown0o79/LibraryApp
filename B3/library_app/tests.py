from .functions import (
    fn_loan_days, fn_book_available_copies,
    fn_book_search, fn_reader_loans, fn_book_availability_report,
)


def run_tests(connection):
    tests = []

    def check(name, condition, details=''):
        tests.append((name, bool(condition), details))

    check('Скалярная функция fn_loan_days', fn_loan_days('2026-10-01', '2026-10-15') == 14)
    check('fn_loan_days с NULL', fn_loan_days(None, '2026-10-15') is None)

    first_book = connection.execute('SELECT book_id FROM books ORDER BY book_id LIMIT 1').fetchone()
    available = fn_book_available_copies(connection, first_book['book_id'])
    check('Скалярная функция доступности', available == 3, f'available={available  }')

    search = fn_book_search(connection, 'Толстой')
    check('Табличная функция поиска', len(search) >= 2, f'найдено={len(search)}')

    reader = connection.execute('SELECT reader_id FROM readers ORDER BY reader_id LIMIT 1').fetchone()
    loans = fn_reader_loans(connection, reader['reader_id'], '2026-01-01', '2026-12-31')
    check('Табличная функция выдачи читателя', len(loans) >= 1, f'выдачи={len(loans)}')

    report = fn_book_availability_report(connection)
    check('Многооператорная табличная функция', len(report) >= 6, f'строк={len(report)}')
    check('Статусы отчёта рассчитаны', all(x['status'] for x in report))

    return tests
