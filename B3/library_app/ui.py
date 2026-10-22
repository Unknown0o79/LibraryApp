import tkinter as tk
from tkinter import ttk, messagebox
from .functions import (
    fn_book_search, fn_reader_loans, fn_book_availability_report,
    fn_book_available_copies, fn_loan_days, register_sql_functions,
)
from .tests import run_tests


class LibraryApp(tk.Tk):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        register_sql_functions(connection)
        self.title('Библиотека — Этап 3: пользовательские функции')
        self.geometry('1050x650')
        self.minsize(900, 560)
        self._build()
        self.show_books()

    def _build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')
        ttk.Label(top, text='БИБЛИОТЕКА', font=('Segoe UI', 18, 'bold')).pack(side='left')
        ttk.Label(top, text='  Этап 3 — пользовательские функции').pack(side='left')

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.books_tab = ttk.Frame(self.tabs, padding=10)
        self.search_tab = ttk.Frame(self.tabs, padding=10)
        self.reader_tab = ttk.Frame(self.tabs, padding=10)
        self.report_tab = ttk.Frame(self.tabs, padding=10)
        self.tests_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.books_tab, text='Книги')
        self.tabs.add(self.search_tab, text='Поиск')
        self.tabs.add(self.reader_tab, text='Выдачи читателя')
        self.tabs.add(self.report_tab, text='Отчёт функций')
        self.tabs.add(self.tests_tab, text='Тестирование')
        self._books_ui(); self._search_ui(); self._reader_ui(); self._report_ui(); self._tests_ui()

    def _tree(self, parent, columns, headings):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True)
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for c, h in zip(columns, headings):
            tree.heading(c, text=h)
            tree.column(c, width=140, anchor='w')
        y = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        x = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        tree.grid(row=0, column=0, sticky='nsew'); y.grid(row=0, column=1, sticky='ns'); x.grid(row=1, column=0, sticky='ew')
        frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
        return tree

    def _books_ui(self):
        bar = ttk.Frame(self.books_tab); bar.pack(fill='x', pady=(0, 8))
        ttk.Button(bar, text='Обновить', command=self.show_books).pack(side='left')
        ttk.Button(bar, text='Проверить выбранную книгу', command=self.selected_available).pack(side='left', padx=8)
        self.books_tree = self._tree(self.books_tab, ('id','title','author','genre','year','copies'), ('ID','Название','Автор','Жанр','Год','Экземпляров'))

    def show_books(self):
        if not hasattr(self, 'books_tree'): return
        self.books_tree.delete(*self.books_tree.get_children())
        rows = self.connection.execute("""SELECT b.book_id,b.title,a.full_name,g.name,b.publish_year,b.total_copies
            FROM books b JOIN authors a ON a.author_id=b.author_id JOIN genres g ON g.genre_id=b.genre_id ORDER BY b.title""").fetchall()
        for r in rows: self.books_tree.insert('', 'end', values=tuple(r))

    def selected_available(self):
        sel = self.books_tree.selection()
        if not sel: return messagebox.showinfo('Информация', 'Выберите книгу.')
        book_id = self.books_tree.item(sel[0])['values'][0]
        n = fn_book_available_copies(self.connection, int(book_id))
        messagebox.showinfo('Скалярная функция', f'Доступно экземпляров: {n}')

    def _search_ui(self):
        bar = ttk.Frame(self.search_tab); bar.pack(fill='x', pady=(0,8))
        self.search_entry = ttk.Entry(bar); self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.insert(0, 'Толстой')
        ttk.Button(bar, text='Найти', command=self.do_search).pack(side='left', padx=8)
        self.search_tree = self._tree(self.search_tab, ('id','title','author','genre','year','copies'), ('ID','Название','Автор','Жанр','Год','Экземпляров'))
        self.do_search()

    def do_search(self):
        if not hasattr(self, 'search_tree'): return
        self.search_tree.delete(*self.search_tree.get_children())
        for r in fn_book_search(self.connection, self.search_entry.get()): self.search_tree.insert('', 'end', values=tuple(r))

    def _reader_ui(self):
        bar = ttk.Frame(self.reader_tab); bar.pack(fill='x', pady=(0,8))
        ttk.Label(bar, text='Читатель:').pack(side='left')
        self.reader_combo = ttk.Combobox(bar, state='readonly', width=35)
        readers = self.connection.execute('SELECT reader_id, full_name FROM readers ORDER BY full_name').fetchall()
        self.reader_map = {r['full_name']: r['reader_id'] for r in readers}
        self.reader_combo['values'] = list(self.reader_map)
        if readers: self.reader_combo.current(0)
        self.reader_combo.pack(side='left', padx=8)
        ttk.Button(bar, text='Показать выдачи', command=self.do_reader_loans).pack(side='left')
        self.reader_tree = self._tree(self.reader_tab, ('id','reader','title','loan','due','return'), ('ID','Читатель','Книга','Дата выдачи','Срок','Возврат'))
        self.do_reader_loans()

    def do_reader_loans(self):
        if not self.reader_combo.get(): return
        rows = fn_reader_loans(self.connection, self.reader_map[self.reader_combo.get()])
        self.reader_tree.delete(*self.reader_tree.get_children())
        for r in rows: self.reader_tree.insert('', 'end', values=tuple(r))

    def _report_ui(self):
        bar = ttk.Frame(self.report_tab); bar.pack(fill='x', pady=(0,8))
        ttk.Button(bar, text='Сформировать отчёт', command=self.do_report).pack(side='left')
        ttk.Label(bar, text='Многооператорная табличная функция: расчёт доступности и статуса.').pack(side='left', padx=12)
        self.report_tree = self._tree(self.report_tab, ('id','title','author','total','issued','available','status'), ('ID','Книга','Автор','Всего','Выдано','Доступно','Статус'))
        self.do_report()

    def do_report(self):
        self.report_tree.delete(*self.report_tree.get_children())
        for r in fn_book_availability_report(self.connection):
            self.report_tree.insert('', 'end', values=(r['book_id'],r['title'],r['author'],r['total_copies'],r['issued'],r['available'],r['status']))

    def _tests_ui(self):
        top = ttk.Frame(self.tests_tab); top.pack(fill='x', pady=(0,8))
        ttk.Button(top, text='Запустить тесты', command=self.do_tests).pack(side='left')
        self.tests_text = tk.Text(self.tests_tab, wrap='word', font=('Consolas', 11))
        self.tests_text.pack(fill='both', expand=True)
        self.do_tests()

    def do_tests(self):
        results = run_tests(self.connection)
        self.tests_text.delete('1.0', 'end')
        passed = sum(ok for _, ok, _ in results)
        for name, ok, details in results:
            self.tests_text.insert('end', f"{'PASS' if ok else 'FAIL'}  {name}  {details}\n")
        self.tests_text.insert('end', f'\nИтог: {passed}/{len(results)} тестов пройдено.')


def run_app(connection):
    app = LibraryApp(connection)
    app.mainloop()
