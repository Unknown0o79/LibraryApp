import tkinter as tk
from tkinter import ttk, messagebox


class LoansView(ttk.Frame):

    def __init__(
        self,
        parent,
        book_service,
        reader_service,
        loan_service,
        refresh_callback=None
    ):
        super().__init__(
            parent,
            padding=10
        )

        self.book_service = book_service
        self.reader_service = reader_service
        self.loan_service = loan_service
        self.refresh_callback = refresh_callback

        self.create_widgets()

    def create_widgets(self):

        toolbar = ttk.Frame(self)

        toolbar.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Button(
            toolbar,
            text="Выдать книгу",
            command=self.create_loan
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            toolbar,
            text="Оформить возврат",
            command=self.return_book
        ).pack(
            side="left",
            padx=4
        )

        columns = (
            "id",
            "book",
            "reader",
            "issue",
            "due",
            "status"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "book": "Книга",
            "reader": "Читатель",
            "issue": "Дата выдачи",
            "due": "Вернуть до",
            "status": "Статус"
        }

        widths = {
            "id": 60,
            "book": 300,
            "reader": 280,
            "issue": 130,
            "due": 130,
            "status": 120
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
            "book",
            anchor="w"
        )

        self.tree.column(
            "reader",
            anchor="w"
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

    def refresh(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        loans = self.loan_service.get_active_loans()

        for loan in loans:
            self.tree.insert(
                "",
                "end",
                values=(
                    loan["id"],
                    loan["title"],
                    loan["full_name"],
                    loan["issue_date"],
                    loan["due_date"],
                    loan["display_status"]
                )
            )

    # =========================================================
    # ВЫДАЧА
    # =========================================================

    def create_loan(self):

        books = self.book_service.get_available_books()

        readers = self.reader_service.get_readers()

        if not books:

            messagebox.showwarning(
                "Нет книг",
                "Нет доступных книг для выдачи."
            )

            return

        if not readers:

            messagebox.showwarning(
                "Нет читателей",
                "Сначала добавьте читателя."
            )

            return

        window = tk.Toplevel(self)

        window.title("Выдача книги")
        window.geometry("600x320")
        window.resizable(False, False)

        window.transient(self)
        window.grab_set()

        frame = ttk.Frame(
            window,
            padding=25
        )

        frame.pack(
            fill="both",expand=True
        )

        # Книга

        ttk.Label(
            frame,
            text="Книга:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=10
        )

        book_values = [
            f"{book['id']} — "
            f"{book['title']} — "
            f"свободно: {book['available']}"
            for book in books
        ]

        book_combo = ttk.Combobox(
            frame,
            values=book_values,
            state="readonly",
            width=55
        )

        book_combo.grid(
            row=0,
            column=1,
            pady=10
        )

        book_combo.current(0)

        # Читатель

        ttk.Label(
            frame,
            text="Читатель:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        reader_values = [
            f"{reader['id']} — "
            f"{reader['full_name']}"
            for reader in readers
        ]

        reader_combo = ttk.Combobox(
            frame,
            values=reader_values,
            state="readonly",
            width=55
        )

        reader_combo.grid(
            row=1,
            column=1,
            pady=10
        )

        reader_combo.current(0)

        # Срок

        ttk.Label(
            frame,
            text="Срок, дней:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=10
        )

        days_entry = ttk.Entry(
            frame,
            width=15
        )

        days_entry.grid(
            row=2,
            column=1,
            sticky="w",
            pady=10
        )

        days_entry.insert(
            0,
            "14"
        )

        def save_loan():

            try:

                book_index = book_combo.current()
                reader_index = reader_combo.current()

                if book_index < 0:
                    raise ValueError(
                        "Выберите книгу."
                    )

                if reader_index < 0:
                    raise ValueError(
                        "Выберите читателя."
                    )

                days = int(
                    days_entry.get()
                )

                self.loan_service.create_loan(
                    books[book_index]["id"],
                    readers[reader_index]["id"],
                    days
                )

                window.destroy()

                self.refresh_all()

                messagebox.showinfo(
                    "Готово",
                    "Книга успешно выдана."
                )

            except ValueError as error:

                messagebox.showerror(
                    "Ошибка",
                    str(error)
                )

        ttk.Button(
            frame,
            text="Оформить выдачу",
            command=save_loan
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            pady=25
        )

    # =========================================================
    # ВОЗВРАТ
    # =========================================================

    def return_book(self):

        selection = self.tree.selection()

        if not selection:

            messagebox.showwarning(
                "Внимание",
                "Выберите выдачу."
            )

            return

        item = self.tree.item(
            selection[0]
        )

        loan_id = item["values"][0]

        answer = messagebox.askyesno(
            "Подтверждение",
            "Оформить возврат выбранной книги?"
        )

        if not answer:
            return

        try:

            self.loan_service.return_book(
                loan_id
            )

            self.refresh_all()

            messagebox.showinfo(
                "Готово",
                "Возврат книги оформлен."
            )

        except ValueError as error:messagebox.showerror(
                "Ошибка",
                str(error)
            )

    def refresh_all(self):

        self.refresh()

        if self.refresh_callback:
            self.refresh_callback()