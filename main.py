# main.py
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from database.db_connection import DatabaseConnection


def main():
    # Создаем подключение к БД
    db = DatabaseConnection("industrial_safety.db")

    # Создаем приложение
    app = QApplication(sys.argv)

    try:
        # Создаем и показываем главное окно
        window = MainWindow(db)
        window.show()

        # Запускаем главный цикл приложения
        sys.exit(app.exec())

    finally:
        # Закрываем соединение с БД
        db.close()


if __name__ == "__main__":
    main()