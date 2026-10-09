import tkinter as tk
from tkinter import ttk, messagebox


class ReaderDialog(tk.Toplevel):

    def __init__(
        self,
        parent,
        reader_service,
        reader=None,
        callback=None
    ):
        super().__init__(parent)

        self.reader_service = reader_service
        self.reader = reader
        self.callback = callback

        self.title(
            "Добавление читателя"
            if reader is None
            else "Редактирование читателя"
        )

        self.geometry("450x330")
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
            ("ФИО:", "full_name"),
            ("Телефон:", "phone"),
            ("Email:", "email")
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
                pady=10
            )

            entry = ttk.Entry(
                frame,
                width=35
            )

            entry.grid(
                row=row,
                column=1,
                pady=10
            )

            self.entries[key] = entry

        if self.reader:

            self.entries["full_name"].insert(
                0,
                self.reader["full_name"]
            )

            self.entries["phone"].insert(
                0,
                self.reader["phone"] or ""
            )

            self.entries["email"].insert(
                0,
                self.reader["email"] or ""
            )

        buttons = ttk.Frame(frame)

        buttons.grid(
            row=3,
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

        full_name = self.entries[
            "full_name"
        ].get().strip()

        phone = self.entries[
            "phone"
        ].get().strip()

        email = self.entries[
            "email"
        ].get().strip()

        try:

            if self.reader:

                self.reader_service.update_reader(
                    self.reader["id"],
                    full_name,
                    phone,
                    email
                )

            else:

                self.reader_service.add_reader(
                    full_name,
                    phone,
                    email
                )

            if self.callback:
                self.callback()

            self.destroy()

        except ValueError as error:

            messagebox.showerror(
                "Ошибка",
                str(error)
            )


class ReadersView(ttk.Frame):

    def __init__(
        self,
        parent,
        reader_service,
        refresh_callback=None
    ):
        super().__init__(
            parent,
            padding=10
        )

        self.reader_service = reader_service
        self.refresh_callback = refresh_callback

        self.create_widgets()

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
            text="Добавить читателя",
            command=self.add_reader
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            toolbar,
            text="Изменить",
            command=self.edit_reader
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            toolbar,
            text="Удалить",
            command=self.delete_reader
        ).pack(
            side="left",
            padx=4
        )

        columns = (
            "id",
            "name",
            "phone",
            "email",
            "registration"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "ФИО",
            "phone": "Телефон",
            "email": "Email",
            "registration": "Дата регистрации"
        }

        widths = {
            "id": 60,
            "name": 300,
            "phone": 180,
            "email": 250,
            "registration": 150
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
            "name",
            anchor="w"
        )

        self.tree.column(
            "email",
            anchor="w"
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

        self.tree.bind(
            "<Double-1>",
            lambda event: self.edit_reader()
        )

    def refresh(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_entry.get().strip()

        readers = self.reader_service.get_readers(
            search
        )

        for reader in readers:

            self.tree.insert(
                "",
                "end",
                values=(
                    reader["id"],
                    reader["full_name"],
                    reader["phone"] or "",
                    reader["email"] or "",
                    reader["registration_date"]
                )
            )

    def get_selected_reader(self):

        selection = self.tree.selection()

        if not selection:

            messagebox.showwarning(
                "Внимание",
                "Выберите читателя."
            )

            return None

        item = self.tree.item(
            selection[0]
        )

        reader_id = item["values"][0]

        for reader in self.reader_service.get_readers():

            if reader["id"] == reader_id:
                return reader

        return None

    def add_reader(self):

        ReaderDialog(
            self,
            self.reader_service,
            callback=self.refresh_all
        )

    def edit_reader(self):

        reader = self.get_selected_reader()

        if reader:

            ReaderDialog(
                self,
                self.reader_service,
                reader=reader,
                callback=self.refresh_all
            )

    def delete_reader(self):

        reader = self.get_selected_reader()

        if not reader:
            return

        answer = messagebox.askyesno(
            "Подтверждение",
            f"Удалить читателя «{reader['full_name']}»?"
        )

        if not answer:
            return

        try:

            self.reader_service.delete_reader(
                reader["id"]
            )

            self.refresh_all()

            messagebox.showinfo(
                "Готово","Читатель удалён."
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