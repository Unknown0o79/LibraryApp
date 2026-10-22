from library_app.db import init_database
from library_app.ui import run_app


def main():
    connection = init_database()
    try:
        run_app(connection)
    finally:
        connection.close()


if __name__ == '__main__':
    main()