import tkinter as tk
from tkinter import ttk, messagebox

from database.database import Database

from services.book_service import BookService
from services.reader_service import ReaderService
from services.loan_service import LoanService

from ui.books_view import BooksView
from ui.readers_view import ReadersView
from ui.loans_view import LoansView
from ui.statistics_view import StatisticsView


class LibraryApplication(tk.Tk):

    def __init__(self):

        super().__init__()

        # =====================================================
        # БАЗА ДАННЫХ
        # =====================================================

        self.database = Database()

        # =====================================================
        # СЕРВИСЫ
        # =====================================================

        self.book_service = BookService(
            self.database
        )

        self.reader_service = ReaderService(
            self.database
        )

        self.loan_service = LoanService(
            self.database
        )

        # =====================================================
        # НАСТРОЙКИ ОКНА
        # =====================================================

        self.title(
            "Информационная система «Библиотека»"
        )

        self.geometry(
            "1200x700"
        )

        self.minsize(
            1000,
            600
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # =====================================================
        # СТИЛИ
        # =====================================================

        self.configure_styles()

        # =====================================================
        # ИНТЕРФЕЙС
        # =====================================================

        self.create_menu()
        self.create_header()
        self.create_notebook()

        self.refresh_all()

    # =========================================================
    # СТИЛИ
    # =========================================================

    def configure_styles(self):

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        style.configure(
            "Subtitle.TLabel",
            font=(
                "Segoe UI",
                10
            )
        )

        style.configure(
            "Treeview",
            rowheight=30,
            font=(
                "Segoe UI",
                10
            )
        )

        style.configure(
            "Treeview.Heading",
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )

        style.configure(
            "TButton",
            padding=6
        )

    # =========================================================
    # МЕНЮ
    # =========================================================

    def create_menu(self):

        menu = tk.Menu(self)

        # Файл

        file_menu = tk.Menu(
            menu,
            tearoff=False
        )

        file_menu.add_command(
            label="Обновить данные",
            command=self.refresh_all
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Выход",
            command=self.on_close
        )

        menu.add_cascade(
            label="Файл",
            menu=file_menu
        )

        # Справка

        help_menu = tk.Menu(
            menu,
            tearoff=False
        )

        help_menu.add_command(
            label="О программе",
            command=self.show_about
        )

        menu.add_cascade(
            label="Справка",
            menu=help_menu
        )

        self.config(menu=menu
        )

    # =========================================================
    # ШАПКА
    # =========================================================

    def create_header(self):

        header = ttk.Frame(
            self,
            padding=(
                20,
                15
            )
        )

        header.pack(
            fill="x"
        )

        ttk.Label(
            header,
            text="📚 БИБЛИОТЕКА",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            header,
            text=(
                "Информационная система "
                "учёта книжного фонда"
            ),
            style="Subtitle.TLabel"
        ).pack(
            anchor="w"
        )

    # =========================================================
    # ВКЛАДКИ
    # =========================================================

    def create_notebook(self):

        self.notebook = ttk.Notebook(
            self
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(
                0,
                15
            )
        )

        # Книги

        self.books_view = BooksView(
            self.notebook,
            self.book_service,
            refresh_callback=self.refresh_statistics
        )

        self.notebook.add(
            self.books_view,
            text="📚 Книги"
        )

        # Читатели

        self.readers_view = ReadersView(
            self.notebook,
            self.reader_service,
            refresh_callback=self.refresh_statistics
        )

        self.notebook.add(
            self.readers_view,
            text="👥 Читатели"
        )

        # Выдача

        self.loans_view = LoansView(
            self.notebook,
            self.book_service,
            self.reader_service,
            self.loan_service,
            refresh_callback=self.refresh_statistics
        )

        self.notebook.add(
            self.loans_view,
            text="📖 Выдача книг"
        )

        # Статистика

        self.statistics_view = StatisticsView(
            self.notebook,
            self.database,
            self.loan_service
        )

        self.notebook.add(
            self.statistics_view,
            text="📊 Статистика"
        )

    # =========================================================
    # ОБНОВЛЕНИЕ
    # =========================================================

    def refresh_all(self):

        self.books_view.refresh()
        self.readers_view.refresh()
        self.loans_view.refresh()
        self.statistics_view.refresh()

    def refresh_statistics(self):

        self.statistics_view.refresh()

    # =========================================================
    # О ПРОГРАММЕ
    # =========================================================

    def show_about(self):

        messagebox.showinfo(
            "О программе",
            "Информационная система «Библиотека»\n\n"
            "Учебный проект по профессиональному модулю ПМ.02.\n\n"
            "Технологии:\n"
            "Python + Tkinter + SQLite\n\n"
            "Основные функции:\n"
            "• учёт книг;\n"
            "• поиск книг;\n"
            "• учёт читателей;\n"
            "• выдача книг;\n"
            "• возврат книг;\n"
            "• контроль сроков;\n"
            "• статистика."
        )

    # =========================================================
    # ЗАКРЫТИЕ
    # =========================================================

    def on_close(self):

        try:
            self.database.close()
        finally:
            self.destroy()