import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("library.db")


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL UNIQUE CHECK(length(trim(full_name)) > 0)
        );
        CREATE TABLE IF NOT EXISTS genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0)
        );
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK(length(trim(title)) > 0),
            author_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            publish_year INTEGER CHECK(publish_year BETWEEN 1450 AND 2100),
            isbn TEXT UNIQUE,
            total_copies INTEGER NOT NULL DEFAULT 1 CHECK(total_copies >= 0),
            FOREIGN KEY(author_id) REFERENCES authors(author_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY(genre_id) REFERENCES genres(genre_id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE TABLE IF NOT EXISTS readers (
            reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            registered_on TEXT NOT NULL DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
            position TEXT NOT NULL DEFAULT 'Библиотекарь'
        );
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL DEFAULT (date('now')),
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Выдана'
                CHECK(status IN ('Выдана','Возвращена','Просрочена')),
            FOREIGN KEY(reader_id) REFERENCES readers(reader_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE TABLE IF NOT EXISTS loan_items (
            loan_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            returned_on TEXT,
            UNIQUE(loan_id, book_id),
            FOREIGN KEY(loan_id) REFERENCES loans(loan_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY(book_id) REFERENCES books(book_id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS ix_books_title ON books(title);
        CREATE INDEX IF NOT EXISTS ix_books_author ON books(author_id);
        CREATE INDEX IF NOT EXISTS ix_loans_date ON loans(loan_date);
        CREATE INDEX IF NOT EXISTS ix_loans_status ON loans(status);
        CREATE INDEX IF NOT EXISTS ix_loans_reader ON loans(reader_id);
        CREATE VIEW IF NOT EXISTS v_book_catalog AS
          SELECT b.book_id, b.title, a.full_name AS author, g.name AS genre,
                 b.publish_year, b.isbn, b.total_copies
          FROM books b JOIN authors a ON a.author_id=b.author_id
          JOIN genres g ON g.genre_id=b.genre_id;
        CREATE VIEW IF NOT EXISTS v_reader_loans AS
          SELECT l.loan_id, r.full_name AS reader, b.title AS book,
                 l.loan_date, l.due_date, l.status, li.returned_on
          FROM loans l JOIN readers r ON r.reader_id=l.reader_id
          JOIN loan_items li ON li.loan_id=l.loan_id
          JOIN books b ON b.book_id=li.book_id;
        CREATE VIEW IF NOT EXISTS v_overdue_loans AS
          SELECT * FROM v_reader_loans
          WHERE status <> 'Возвращена' AND due_date < date('now');
        """)

        # Seed only an empty database; re-running the program does not duplicate data.
        if con.execute("SELECT COUNT(*) FROM authors").fetchone()[0] == 0:
            authors = ["Александр Пушкин", "Фёдор Достоевский", "Лев Толстой",
                       "Антон Чехов", "Михаил Булгаков", "Николай Гоголь",
                       "Иван Тургенев", "Агата Кристи", "Джордж Оруэлл", "Рэй Брэдбери"]
            genres = ["Классика", "Роман", "Повесть", "Детектив", "Фантастика",
                      "Драма", "Приключения", "Поэзия", "Антиутопия", "Рассказ"]
            con.executemany("INSERT INTO authors(full_name) VALUES (?)", [(x,) for x in authors])
            con.executemany("INSERT INTO genres(name) VALUES (?)", [(x,) for x in genres])
            books = [
                ("Евгений Онегин",1,8,1833,"978-5-00001-001-1",4),
                ("Преступление и наказание",2,2,1866,"978-5-00001-002-8",3),
                ("Война и мир",3,2,1869,"978-5-00001-003-5",5),
                ("Вишнёвый сад",4,6,1904,"978-5-00001-004-2",2),
                ("Мастер и Маргарита",5,2,1967,"978-5-00001-005-9",4),
                ("Мёртвые души",6,1,1842,"978-5-00001-006-6",3),
                ("Отцы и дети",7,2,1862,"978-5-00001-007-3",2),
                ("Убийство в Восточном экспрессе",8,4,1934,"978-5-00001-008-0",3),
                ("1984",9,9,1949,"978-5-00001-009-7",4),
                ("451 градус по Фаренгейту",10,5,1953,"978-5-00001-010-3",3),
            ]
            con.executemany("""INSERT INTO books(title,author_id,genre_id,publish_year,isbn,total_copies)
                               VALUES (?,?,?,?,?,?)""", books)
            readers = [
                ("Анна Смирнова","+7-900-000-01-01","anna@example.com"),
                ("Иван Петров","+7-900-000-01-02","ivan@example.com"),
                ("Мария Иванова","+7-900-000-01-03","maria@example.com"),
                ("Алексей Соколов","+7-900-000-01-04","alex@example.com"),
                ("Елена Кузнецова","+7-900-000-01-05","elena@example.com"),
                ("Дмитрий Попов","+7-900-000-01-06","dmitry@example.com"),
                ("Ольга Васильева","+7-900-000-01-07","olga@example.com"),
                ("Сергей Павлов","+7-900-000-01-08","sergey@example.com"),
                ("Наталья Семёнова","+7-900-000-01-09","natalia@example.com"),
                ("Павел Фёдоров","+7-900-000-01-10","pavel@example.com"),
            ]
            con.executemany("INSERT INTO readers(full_name,phone,email) VALUES (?,?,?)", readers)
            con.executemany("INSERT INTO employees(full_name,position) VALUES (?,?)",
                            [("Ирина Белова","Старший библиотекарь"),
                             ("Олег Морозов","Библиотекарь")])
            today = date.today()
            loans = []
            # 20 demonstration issue records, with dates spread over the last month.
            for i in range(20):
                reader_id = (i % 10) + 1
                employee_id = (i % 2) + 1
                loan_date = today - timedelta(days=(i % 25) + 1)
                due_date = loan_date + timedelta(days=14)
                status = "Возвращена" if i % 4 == 0 else "Выдана"
                loans.append((reader_id, employee_id, loan_date.isoformat(), due_date.isoformat(), status))
            con.executemany("""INSERT INTO loans(reader_id,employee_id,loan_date,due_date,status)
                               VALUES (?,?,?,?,?)""", loans)
            items = []
            for i in range(20):
                items.append((i+1, (i % 10)+1, (date.today()-timedelta(days=1)).isoformat()
                              if i % 4 == 0 else None))
            con.executemany("INSERT INTO loan_items(loan_id,book_id,returned_on) VALUES (?,?,?)", items)


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Информационная система библиотеки")
        self.geometry("1120x700")
        self.minsize(900, 560)
        self.configure(padx=12, pady=10)
        self._build_ui()
        self.refresh_books()
        self.refresh_loans()
        self.refresh_readers()

    def _build_ui(self):
        ttk.Label(self, text="Информационная система библиотеки",
                  font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 10))
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)
        self.book_tab = ttk.Frame(tabs, padding=10)
        self.reader_tab = ttk.Frame(tabs, padding=10)
        self.loan_tab = ttk.Frame(tabs, padding=10)
        self.report_tab = ttk.Frame(tabs, padding=10)
        tabs.add(self.book_tab, text="Каталог книг")
        tabs.add(self.reader_tab, text="Читатели")
        tabs.add(self.loan_tab, text="Выдачи")
        tabs.add(self.report_tab, text="Отчёты")
        self._build_books()
        self._build_readers()
        self._build_loans()
        self._build_reports()

    def make_tree(self, parent, columns, headings, widths=None):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)
        for i, (col, heading) in enumerate(zip(columns, headings)):
            tree.heading(col, text=heading)
            tree.column(col, width=(widths[i] if widths else 130), anchor="w")
        tree.pack(fill="both", expand=True, pady=(8, 0))
        return tree

    def _build_books(self):
        bar = ttk.Frame(self.book_tab); bar.pack(fill="x")
        ttk.Label(bar, text="Поиск по названию или автору:").pack(side="left")
        self.book_search = tk.StringVar()
        ttk.Entry(bar, textvariable=self.book_search, width=32).pack(side="left", padx=6)
        ttk.Button(bar, text="Найти", command=self.refresh_books).pack(side="left")
        ttk.Button(bar, text="Показать все", command=lambda: (self.book_search.set(""), self.refresh_books())).pack(side="left", padx=5)
        ttk.Button(bar, text="Добавить книгу", command=self.add_book_dialog).pack(side="right")
        self.books_tree = self.make_tree(self.book_tab,
            ("id","title","author","genre","year","copies"),
            ("ID","Название","Автор","Жанр","Год","Экземпляров"), (45,300,220,140,70,100))

    def _build_readers(self):
        bar = ttk.Frame(self.reader_tab); bar.pack(fill="x")
        ttk.Button(bar, text="Добавить читателя", command=self.add_reader_dialog).pack(side="left")
        ttk.Button(bar, text="Обновить", command=self.refresh_readers).pack(side="left", padx=6)
        self.readers_tree = self.make_tree(self.reader_tab,
            ("id","name","phone","email","registered"),
            ("ID","ФИО","Телефон","Электронная почта","Дата регистрации"), (50,230,170,260,130))

    def _build_loans(self):
        bar = ttk.Frame(self.loan_tab); bar.pack(fill="x")
        ttk.Button(bar, text="Выдать книгу", command=self.issue_book_dialog).pack(side="left")
        ttk.Button(bar, text="Вернуть выбранную выдачу", command=self.return_loan).pack(side="left", padx=6)
        ttk.Button(bar, text="Обновить", command=self.refresh_loans).pack(side="left")
        self.loans_tree = self.make_tree(self.loan_tab,
            ("id","reader","book","loan_date","due_date","status"),
            ("ID","Читатель","Книга","Дата выдачи","Вернуть до","Статус"), (50,200,270,120,120,120))

    def _build_reports(self):
        bar = ttk.Frame(self.report_tab); bar.pack(fill="x")
        ttk.Button(bar, text="Каталог книг", command=lambda: self.show_report("catalog")).pack(side="left")
        ttk.Button(bar, text="История выдач", command=lambda: self.show_report("loans")).pack(side="left", padx=5)
        ttk.Button(bar, text="Просроченные выдачи", command=lambda: self.show_report("overdue")).pack(side="left")
        ttk.Label(self.report_tab, text="Отчёты формируются из SQL-представлений базы данных.",
                  foreground="#555").pack(anchor="w", pady=(10,0))
        self.report_tree = self.make_tree(self.report_tab, ("c1","c2","c3","c4","c5","c6"),
                                          ("Поле 1","Поле 2","Поле 3","Поле 4","Поле 5","Поле 6"),
                                          (120,180,230,150,150,130))

    def refresh_books(self):
        for x in self.books_tree.get_children(): self.books_tree.delete(x)
        q = "%" + self.book_search.get().strip() + "%"
        with connect() as con:
            rows = con.execute("""SELECT book_id,title,author,genre,publish_year,total_copies
                                  FROM v_book_catalog WHERE title LIKE ? OR author LIKE ?
                                  ORDER BY title""", (q,q)).fetchall()
        for r in rows: self.books_tree.insert("", "end", values=tuple(r))

    def refresh_readers(self):
        for x in self.readers_tree.get_children(): self.readers_tree.delete(x)
        with connect() as con:
            rows = con.execute("SELECT reader_id,full_name,phone,email,registered_on FROM readers ORDER BY full_name").fetchall()
        for r in rows: self.readers_tree.insert("", "end", values=tuple(r))

    def refresh_loans(self):
        for x in self.loans_tree.get_children(): self.loans_tree.delete(x)
        with connect() as con:
            rows = con.execute("""SELECT loan_id,reader,book,loan_date,due_date,status
                                  FROM v_reader_loans ORDER BY loan_id DESC""").fetchall()
        for r in rows: self.loans_tree.insert("", "end", values=tuple(r))

    def add_book_dialog(self):
        self.simple_dialog("Добавить книгу",
            [("Название","title"),("Автор (ФИО)","author"),("Жанр","genre"),
             ("Год издания","year"),("ISBN","isbn"),("Количество экземпляров","copies")],
            self.save_book)

    def save_book(self, v):
        try:
            year = int(v["year"]) if v["year"].strip() else None
            copies = int(v["copies"])
            with connect() as con:
                con.execute("INSERT OR IGNORE INTO authors(full_name) VALUES (?)",(v["author"].strip(),))
                con.execute("INSERT OR IGNORE INTO genres(name) VALUES (?)",(v["genre"].strip(),))
                aid = con.execute("SELECT author_id FROM authors WHERE full_name=?",(v["author"].strip(),)).fetchone()[0]
                gid = con.execute("SELECT genre_id FROM genres WHERE name=?",(v["genre"].strip(),)).fetchone()[0]
                con.execute("""INSERT INTO books(title,author_id,genre_id,publish_year,isbn,total_copies)
                               VALUES (?,?,?,?,?,?)""",
                            (v["title"].strip(),aid,gid,year,v["isbn"].strip() or None,copies))
            self.refresh_books()
            messagebox.showinfo("Готово","Книга добавлена.")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка",f"Не удалось добавить книгу:\n{e}")
            return False

    def add_reader_dialog(self):
        self.simple_dialog("Добавить читателя",
            [("ФИО","name"),("Телефон","phone"),("Электронная почта","email")],
            self.save_reader)

    def save_reader(self, v):
        try:
            with connect() as con:
                con.execute("INSERT INTO readers(full_name,phone,email) VALUES (?,?,?)",
                            (v["name"].strip(),v["phone"].strip() or None,v["email"].strip() or None))
            self.refresh_readers()
            messagebox.showinfo("Готово","Читатель добавлен.")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка",f"Не удалось добавить читателя:\n{e}")
            return False

    def simple_dialog(self, title, fields, callback):
        win = tk.Toplevel(self); win.title(title); win.transient(self); win.grab_set()
        entries = {}
        for i,(label,key) in enumerate(fields):
            ttk.Label(win,text=label).grid(row=i,column=0,sticky="w",padx=10,pady=6)
            ent=ttk.Entry(win,width=38); ent.grid(row=i,column=1,padx=10,pady=6); entries[key]=ent
        if "copies" in entries: entries["copies"].insert(0,"1")
        def submit():
            vals={k:e.get() for k,e in entries.items()}
            if any(not vals[k].strip() for k in vals if k not in ("isbn","phone","email","year")):
                messagebox.showwarning("Проверка","Заполните обязательные поля.",parent=win); return
            if callback(vals): win.destroy()
        ttk.Button(win,text="Сохранить",command=submit).grid(row=len(fields),column=0,columnspan=2,pady=10)

    def issue_book_dialog(self):
        with connect() as con:
            readers=con.execute("SELECT reader_id,full_name FROM readers ORDER BY full_name").fetchall()
            books=con.execute("SELECT book_id,title,total_copies FROM books ORDER BY title").fetchall()
            employees=con.execute("SELECT employee_id,full_name FROM employees ORDER BY full_name").fetchall()
        if not readers or not books or not employees:
            messagebox.showwarning("Нет данных","Сначала добавьте читателя, книгу и сотрудника."); return
        win=tk.Toplevel(self); win.title("Выдать книгу"); win.transient(self); win.grab_set()
        ttk.Label(win,text="Читатель").grid(row=0,column=0,padx=10,pady=7,sticky="w")
        rvar=tk.StringVar(value=readers[0]["full_name"])
        ttk.Combobox(win,textvariable=rvar,values=[r["full_name"] for r in readers],state="readonly",width=36).grid(row=0,column=1,padx=10,pady=7)
        ttk.Label(win,text="Книга").grid(row=1,column=0,padx=10,pady=7,sticky="w")
        bvar=tk.StringVar(value=books[0]["title"])
        ttk.Combobox(win,textvariable=bvar,values=[b["title"] for b in books],state="readonly",width=36).grid(row=1,column=1,padx=10,pady=7)
        ttk.Label(win,text="Сотрудник").grid(row=2,column=0,padx=10,pady=7,sticky="w")
        evar=tk.StringVar(value=employees[0]["full_name"])
        ttk.Combobox(win,textvariable=evar,values=[e["full_name"] for e in employees],state="readonly",width=36).grid(row=2,column=1,padx=10,pady=7)
        ttk.Label(win,text="Срок возврата (ГГГГ-ММ-ДД)").grid(row=3,column=0,padx=10,pady=7,sticky="w")
        dvar=tk.StringVar(value=(date.today()+timedelta(days=14)).isoformat())
        ttk.Entry(win,textvariable=dvar,width=39).grid(row=3,column=1,padx=10,pady=7)
        def submit():
            try:
                due=date.fromisoformat(dvar.get().strip()).isoformat()
                with connect() as con:
                    rid=con.execute("SELECT reader_id FROM readers WHERE full_name=?",(rvar.get(),)).fetchone()[0]
                    bid=con.execute("SELECT book_id,total_copies FROM books WHERE title=?",(bvar.get(),)).fetchone()
                    eid=con.execute("SELECT employee_id FROM employees WHERE full_name=?",(evar.get(),)).fetchone()[0]
                    active=con.execute("""SELECT COUNT(*) FROM loan_items li JOIN loans l ON l.loan_id=li.loan_id
                                          WHERE li.book_id=? AND l.status<>'Возвращена'""",(bid["book_id"],)).fetchone()[0]
                    if active >= bid["total_copies"]:
                        raise ValueError("Нет свободных экземпляров этой книги.")
                    cur=con.execute("INSERT INTO loans(reader_id,employee_id,due_date,status) VALUES (?,?,?,'Выдана')",
                                    (rid,eid,due))
                    con.execute("INSERT INTO loan_items(loan_id,book_id) VALUES (?,?)",(cur.lastrowid,bid["book_id"]))
                win.destroy(); self.refresh_loans(); messagebox.showinfo("Готово","Выдача оформлена.")
            except Exception as ex: messagebox.showerror("Ошибка",str(ex),parent=win)
        ttk.Button(win,text="Оформить выдачу",command=submit).grid(row=4,column=0,columnspan=2,pady=10)

    def return_loan(self):
        selected=self.loans_tree.selection()
        if not selected:
            messagebox.showwarning("Выбор","Выберите выдачу в таблице."); return
        loan_id=self.loans_tree.item(selected[0],"values")[0]
        try:
            with connect() as con:
                con.execute("UPDATE loans SET status='Возвращена' WHERE loan_id=?",(loan_id,))
                con.execute("UPDATE loan_items SET returned_on=? WHERE loan_id=?",
                            (date.today().isoformat(),loan_id))
            self.refresh_loans()
            messagebox.showinfo("Готово","Книга отмечена как возвращённая.")
        except Exception as e: messagebox.showerror("Ошибка",str(e))

    def show_report(self, kind):
        for x in self.report_tree.get_children(): self.report_tree.delete(x)
        with connect() as con:
            if kind=="catalog":
                headings=("ID","Название","Автор","Жанр","Год","Экземпляров")
                rows=con.execute("SELECT book_id,title,author,genre,publish_year,total_copies FROM v_book_catalog ORDER BY title").fetchall()
            elif kind=="overdue":
                headings=("ID","Читатель","Книга","Дата выдачи","Срок возврата","Статус")
                rows=con.execute("SELECT loan_id,reader,book,loan_date,due_date,status FROM v_overdue_loans ORDER BY due_date").fetchall()
            else:
                headings=("ID","Читатель","Книга","Дата выдачи","Срок возврата","Статус")
                rows=con.execute("SELECT loan_id,reader,book,loan_date,due_date,status FROM v_reader_loans ORDER BY loan_id DESC").fetchall()
        for i,h in enumerate(headings): self.report_tree.heading(f"c{i+1}",text=h)
        for r in rows: self.report_tree.insert("","end",values=tuple(r))

if __name__ == "__main__":
    init_db()
    app = LibraryApp()
    app.mainloop()
