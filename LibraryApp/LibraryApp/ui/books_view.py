import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


class BookDialog(tk.Toplevel):

    def __init__(
        self,
        parent,
        book_service,
        book=None,
        callback=None
    ):
        super().__init__(parent)

        self.book_service = book_service
        self.book = book
        self.callback = callback

        if book is None:
            self.title("Добавление книги")
        else:
            self.title("Редактирование книги")

        self.geometry("500x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(
            self,
            padding=20
        )

        frame.pack(
            fill="both",
            expand=True
        )

        fields = [
            ("Название:", "title"),
            ("Автор:", "author"),
            ("ISBN:", "isbn"),
            ("Жанр:", "genre"),
            ("Год издания:", "year"),
            ("Издательство:", "publisher"),
            ("Количество:", "quantity")
        ]

        self.entries = {}

        for row, (label, key) in enumerate(fields):

            ttk.Label(
                frame,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=7
            )

            entry = ttk.Entry(
                frame,
                width=38
            )

            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                pady=7
            )

            self.entries[key] = entry

        if self.book:
            values = {
                "title": self.book["title"],
                "author": self.book["author"],
                "isbn": self.book["isbn"] or "",
                "genre": self.book["genre"] or "",
                "year": self.book["year"] or "",
                "publisher": self.book["publisher"] or "",
                "quantity": self.book["quantity"]
            }

            for key, value in values.items():
                self.entries[key].insert(
                    0,
                    str(value)
                )

        buttons = ttk.Frame(frame)

        buttons.grid(
            row=len(fields),
            column=0,
            columnspan=2,
            pady=25
        )

        ttk.Button(
            buttons,
            text="Сохранить",
            command=self.save
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            buttons,
            text="Отмена",
            command=self.destroy
        ).pack(
            side="left",
            padx=5
        )

    def save(self):
        try:
            title = self.entries["title"].get().strip()
            author = self.entries["author"].get().strip()
            isbn = self.entries["isbn"].get().strip()
            genre = self.entries["genre"].get().strip()
            year = self.entries["year"].get().strip()
            publisher = self.entries["publisher"].get().strip()
            quantity = self.entries["quantity"].get().strip()

            year_value = int(year) if year else None
            quantity_value = int(quantity)

            if self.book:
                self.book_service.update_book(
                    self.book["id"],
                    title,
                    author,
                    isbn,
                    genre,
                    year_value,
                    publisher,
                    quantity_value
                )
            else:
                self.book_service.add_book(
                    title,
                    author,
                    isbn,
                    genre,
                    year_value,
                    publisher,
                    quantity_value
                )

            if self.callback:
                self.callback()
                self.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Ошибка",
                "Книга с таким ISBN уже существует."
            )

        except ValueError as error:
            messagebox.showerror(
                "Ошибка",
                str(error)
            )


class BooksView(ttk.Frame):

    def __init__(
        self,
        parent,
        book_service,
        refresh_callback=None
    ):
        super().__init__(
            parent,
            padding=10
        )

        self.book_service = book_service
        self.refresh_callback = refresh_callback

        self.create_widgets()

    # =========================================================
    # СОЗДАНИЕ ИНТЕРФЕЙСА
    # =========================================================

    def create_widgets(self):

        toolbar = ttk.Frame(self)

        toolbar.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            toolbar,
            text="Поиск:"
        ).pack(
            side="left"
        )

        self.search_entry = ttk.Entry(
            toolbar,
            width=35
        )

        self.search_entry.pack(
            side="left",
            padx=8
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh()
        )

        ttk.Button(
            toolbar,
            text="Добавить книгу",
            command=self.add_book
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            toolbar,
            text="Изменить",
            command=self.edit_book
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            toolbar,
            text="Удалить",
            command=self.delete_book
        ).pack(
            side="left",
            padx=4
        )

        columns = (
            "id",
            "title",
            "author",
            "isbn",
            "genre",
            "year",
            "quantity",
            "available"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "title": "Название",
            "author": "Автор",
            "isbn": "ISBN",
            "genre": "Жанр",
            "year": "Год",
            "quantity": "Всего",
            "available": "Свободно"
        }

        widths = {
            "id": 50,
            "title": 220,
            "author": 180,
            "isbn": 140,
            "genre": 130,
            "year": 70,
            "quantity": 70,
            "available": 80
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.tree.column(
            "title",
            anchor="w"
        )

        self.tree.column(
            "author",
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<Double-1>",
            lambda event: self.edit_book()
        )

    # =========================================================
    # ОБНОВЛЕНИЕ
    # =========================================================

    def refresh(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_entry.get().strip()
        books = self.book_service.get_books(search)

        for book in books:

            self.tree.insert(
                "",
                "end",
                values=(
                    book["id"],
                    book["title"],
                    book["author"],
                    book["isbn"] or "",
                    book["genre"] or "",
                    book["year"] or "",
                    book["quantity"],
                    book["available"]
                )
            )

    # =========================================================
    # ВЫБОР КНИГИ
    # =========================================================

    def get_selected_book(self):

        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning(
                "Внимание",
                "Выберите книгу."
            )
            return None

        item = self.tree.item(
            selection[0]
        )

        book_id = item["values"][0]

        for book in self.book_service.get_books():

            if book["id"] == book_id:
                return book

        return None

    # =========================================================
    # ДОБАВЛЕНИЕ
    # =========================================================

    def add_book(self):

        BookDialog(
            self,
            self.book_service,
            callback=self.refresh_all
        )

    # =========================================================
    # РЕДАКТИРОВАНИЕ
    # =========================================================

    def edit_book(self):

        book = self.get_selected_book()

        if book:

            BookDialog(
                self,
                self.book_service,
                book=book,
                callback=self.refresh_all
            )

    # =========================================================
    # УДАЛЕНИЕ
    # =========================================================

    def delete_book(self):

        book = self.get_selected_book()

        if not book:
            return

        answer = messagebox.askyesno(
            "Подтверждение",
            f"Удалить книгу «{book['title']}»?"
        )

        if not answer:
            return

        try:

            self.book_service.delete_book(
                book["id"]
            )

            self.refresh_all()

            messagebox.showinfo(
                "Готово",
                "Книга удалена."
            )

        except ValueError as error:

            messagebox.showerror(
                "Ошибка",
                str(error)
            )

    def refresh_all(self):

        self.refresh()

        if self.refresh_callback:
            self.refresh_callback()