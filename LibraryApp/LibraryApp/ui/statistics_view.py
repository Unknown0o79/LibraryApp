import tkinter as tk
from tkinter import ttk


class StatisticsView(ttk.Frame):

    def __init__(
        self,
        parent,
        database,
        loan_service
    ):
        super().__init__(
            parent,
            padding=30
        )

        self.database = database
        self.loan_service = loan_service

        self.statistics_labels = {}

        self.create_widgets()

    def create_widgets(self):

        statistics = [
            ("books", "Наименований книг"),
            ("copies", "Всего экземпляров"),
            ("available", "Свободных экземпляров"),
            ("readers", "Читателей"),
            ("loans", "Книг на руках"),
            ("overdue", "Просроченных выдач")
        ]

        for row, (key, title) in enumerate(statistics):

            card = ttk.LabelFrame(
                self,
                text=title,
                padding=20
            )

            card.grid(
                row=row // 3,
                column=row % 3,
                padx=15,
                pady=15,
                sticky="nsew"
            )

            label = ttk.Label(
                card,
                text="0",
                font=("Segoe UI", 24, "bold")
            )

            label.pack(
                padx=30,
                pady=20
            )

            self.statistics_labels[key] = label

        for column in range(3):

            self.columnconfigure(
                column,
                weight=1
            )

        for row in range(2):

            self.rowconfigure(
                row,
                weight=1
            )

    def refresh(self):

        cursor = self.database.connection.cursor()

        # Количество наименований и экземпляров

        cursor.execute("""
            SELECT
                COUNT(*) AS total_books,
                COALESCE(SUM(quantity), 0) AS total_copies,
                COALESCE(SUM(available), 0) AS available_copies
            FROM books
        """)

        books = cursor.fetchone()

        # Количество читателей

        cursor.execute("""
            SELECT COUNT(*)
            FROM readers
        """)

        readers = cursor.fetchone()[0]

        # Книги на руках

        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE status = 'Выдана'
        """)

        loans = cursor.fetchone()[0]

        # Просроченные

        overdue = self.loan_service.get_overdue_count()

        values = {
            "books": books["total_books"],
            "copies": books["total_copies"],
            "available": books["available_copies"],
            "readers": readers,
            "loans": loans,
            "overdue": overdue
        }

        for key, value in values.items():

            self.statistics_labels[key].config(
                text=str(value)
            )