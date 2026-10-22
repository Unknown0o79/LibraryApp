import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

DB = Path(__file__).with_name("LibraryDB.db")


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Информационная система библиотеки — Этап 4")
        self.geometry("1100x700")
        self.minsize(950, 600)

        self.conn = sqlite3.connect(DB)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(
            top,
            text="ИНФОРМАЦИОННАЯ СИСТЕМА БИБЛИОТЕКИ — ЭТАП 4",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")
        ttk.Button(top, text="Обновить", command=self.refresh_all).pack(side="right")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_books = ttk.Frame(self.nb, padding=8)
        self.tab_readers = ttk.Frame(self.nb, padding=8)
        self.tab_audit = ttk.Frame(self.nb, padding=8)
        self.tab_triggers = ttk.Frame(self.nb, padding=8)
        self.tab_demo = ttk.Frame(self.nb, padding=8)

        self.nb.add(self.tab_books, text="Книги")
        self.nb.add(self.tab_readers, text="Читатели")
        self.nb.add(self.tab_audit, text="Аудит")
        self.nb.add(self.tab_triggers, text="Триггеры")
        self.nb.add(self.tab_demo, text="Демонстрация")

        self.build_books()
        self.build_readers()
        self.build_audit()
        self.build_triggers()
        self.build_demo()

        status = ttk.Label(self, text=f"База данных: {DB}", relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

    def make_tree(self, parent, columns, headings, widths=None):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for i, c in enumerate(columns):
            tree.heading(c, text=headings[i])
            tree.column(c, width=(widths[i] if widths else 130), anchor="w")
        y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y.grid(row=0, column=1, sticky="ns")
        x.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def build_books(self):
        bar = ttk.Frame(self.tab_books)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Показать каталог", command=self.load_books).pack(side="left")
        ttk.Button(bar, text="Изменить экземпляры +1", command=self.audit_update_book).pack(side="left", padx=5)
        ttk.Button(bar, text="Архивировать книгу", command=self.archive_selected).pack(side="left", padx=5)
        self.books_tree = self.make_tree(
            self.tab_books,
            ("book_id","title","author","genre","year","isbn","copies","archived"),
            ("ID","Название","Автор","Жанр","Год","ISBN","Экземпляры","Архив"),
            [50,240,180,130,70,150,90,70]
        )
        self.load_books()

    def build_readers(self):
        bar = ttk.Frame(self.tab_readers)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Обновить", command=self.load_readers).pack(side="left")
        ttk.Button(bar, text="Добавить тестового читателя", command=self.insert_test_reader).pack(side="left", padx=5)
        ttk.Button(bar, text="Изменить тестового читателя", command=self.update_test_reader).pack(side="left", padx=5)
        ttk.Button(bar, text="Удалить тестового читателя", command=self.delete_test_reader).pack(side="left", padx=5)
        self.readers_tree = self.make_tree(
            self.tab_readers,
            ("reader_id","full_name","phone","email","registered_on"),
            ("ID","ФИО","Телефон","E-mail","Дата регистрации"),
            [60,240,150,240,130]
        )
        self.load_readers()

    def build_audit(self):
        bar = ttk.Frame(self.tab_audit)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Обновить журнал", command=self.load_audit).pack(side="left")
        ttk.Button(bar, text="Очистить журнал", command=self.clear_audit).pack(side="left", padx=5)
        self.audit_tree = self.make_tree(
            self.tab_audit,
            ("audit_id","table_name","operation","row_id","old_data","new_data","actor","changed_at"),
            ("ID","Таблица","Операция","Row ID","Старые данные","Новые данные","Источник","Дата/время"),
            [50,100,90,70,260,260,110,160]
        )
        self.load_audit()

    def build_triggers(self):
        ttk.Label(
            self.tab_triggers,
            text="Триггеры этапа 4, созданные в LibraryDB.db",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0,8))
        self.trigger_tree = self.make_tree(
            self.tab_triggers,
            ("name","table_name","sql"),
            ("Название","Объект","SQL"),
            [260,180,650]
        )
        self.load_triggers()

    def build_demo(self):
        ttk.Label(
            self.tab_demo,
            text="Проверка триггеров из UI Visual Studio",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")
        ttk.Label(
            self.tab_demo,
            text="Эта вкладка выполняет те же действия, которые можно выполнить вручную в Letos."
        ).pack(anchor="w", pady=(3,15))

        buttons = ttk.Frame(self.tab_demo)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="1. AFTER UPDATE — аудит книги", command=self.audit_update_book).pack(fill="x", pady=4)
        ttk.Button(buttons, text="2. INSERT — аудит читателя", command=self.insert_test_reader).pack(fill="x", pady=4)
        ttk.Button(buttons, text="3. UPDATE — аудит читателя", command=self.update_test_reader).pack(fill="x", pady=4)
        ttk.Button(buttons, text="4. DELETE — аудит читателя", command=self.delete_test_reader).pack(fill="x", pady=4)
        ttk.Button(buttons, text="5. INSTEAD OF DELETE — архивирование", command=self.archive_selected).pack(fill="x", pady=4)
        ttk.Button(buttons, text="6. Обновить журнал аудита", command=self.load_audit).pack(fill="x", pady=4)

        self.log = tk.Text(self.tab_demo, height=18, wrap="word")
        self.log.pack(fill="both", expand=True, pady=(12,0))
        self.log.insert("end", "Готово. Выберите действие.\n")

    def log_msg(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def load_books(self):
        for x in self.books_tree.get_children(): self.books_tree.delete(x)
        rows = self.conn.execute("""
            SELECT b.book_id,b.title,
                   COALESCE(a.full_name,'') author,
                   COALESCE(g.name,'') genre,
                   b.publish_year,b.isbn,b.total_copies,b.is_archived
            FROM books b
            LEFT JOIN authors a ON a.author_id=b.author_id
            LEFT JOIN genres g ON g.genre_id=b.genre_id
            ORDER BY b.book_id
        """).fetchall()
        for r in rows:
            self.books_tree.insert("", "end", values=tuple(r))

    def load_readers(self):
        for x in self.readers_tree.get_children(): self.readers_tree.delete(x)
        rows = self.conn.execute("SELECT reader_id,full_name,phone,email,registered_on FROM readers ORDER BY reader_id").fetchall()
        for r in rows:
            self.readers_tree.insert("", "end", values=tuple(r))

    def load_audit(self):
        for x in self.audit_tree.get_children(): self.audit_tree.delete(x)
        rows = self.conn.execute("""
            SELECT audit_id,table_name,operation,row_id,COALESCE(old_data,''),
                   COALESCE(new_data,''),actor,changed_at
            FROM audit_changes ORDER BY audit_id DESC
        """).fetchall()
        for r in rows:
            self.audit_tree.insert("", "end", values=tuple(r))

    def load_triggers(self):
        for x in self.trigger_tree.get_children(): self.trigger_tree.delete(x)
        rows = self.conn.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type='trigger'
            ORDER BY name
        """).fetchall()
        for r in rows:
            self.trigger_tree.insert("", "end", values=tuple(r))

    def audit_update_book(self):
        try:
            self.conn.execute("UPDATE books SET total_copies=total_copies+1 WHERE book_id=1")
            self.conn.commit()
            self.log_msg("AFTER UPDATE: книга ID 1 изменена, запись добавлена в audit_changes.")
            self.load_books()
            self.load_audit()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def insert_test_reader(self):
        try:
            # Remove a previous demo reader so the button can be pressed repeatedly.
            self.conn.execute("DELETE FROM readers WHERE email='stage4_demo@library.local'")
            self.conn.execute("""
                INSERT INTO readers(full_name,phone,email,registered_on)
                VALUES ('Тестовый читатель Этап 4','+79990000004','stage4_demo@library.local',date('now'))
            """)
            self.conn.commit()
            self.log_msg("AFTER INSERT: тестовый читатель добавлен, аудит записан.")
            self.load_readers()
            self.load_audit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", str(e))

    def update_test_reader(self):
        try:
            cur = self.conn.execute("""
                UPDATE readers SET phone='+79990000005'
                WHERE email='stage4_demo@library.local'
            """)
            self.conn.commit()
            if cur.rowcount:
                self.log_msg("AFTER UPDATE: тестовый читатель изменён, аудит записан.")
            else:
                self.log_msg("Сначала нажмите «Добавить тестового читателя».")
            self.load_readers()
            self.load_audit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", str(e))

    def delete_test_reader(self):
        try:
            cur = self.conn.execute("""
                DELETE FROM readers WHERE email='stage4_demo@library.local'
            """)
            self.conn.commit()
            if cur.rowcount:
                self.log_msg("AFTER DELETE: тестовый читатель удалён, аудит записан.")
            else:
                self.log_msg("Тестовый читатель не найден.")
            self.load_readers()
            self.load_audit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", str(e))

    def archive_selected(self):
        selected = self.books_tree.selection()
        if selected:
            vals = self.books_tree.item(selected[0], "values")
            book_id = vals[0]
        else:
            book_id = "10"
        try:
            self.conn.execute("DELETE FROM v_active_books WHERE book_id=?", (book_id,))
            self.conn.commit()
            self.log_msg(f"INSTEAD OF DELETE: книга ID {book_id} переведена в архив (is_archived=1).")
            self.load_books()
            self.load_audit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", str(e))

    def clear_audit(self):
        if messagebox.askyesno("Подтверждение", "Очистить журнал аудита?"):
            self.conn.execute("DELETE FROM audit_changes")
            self.conn.commit()
            self.load_audit()
            self.log_msg("Журнал аудита очищен.")

    def refresh_all(self):
        self.load_books()
        self.load_readers()
        self.load_audit()
        self.load_triggers()

    def on_close(self):
        self.conn.close()
        self.destroy()


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
