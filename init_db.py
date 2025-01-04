# init_db.py
import os
from database.db_connection import DatabaseConnection


def init_database():
    """Инициализация базы данных"""
    # Определяем пути к файлам
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'industrial_safety.db')
    schema_path = os.path.join(current_dir, 'schema.sql')

    # Создаем папку database если её нет
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Удаляем старую БД если она существует
    if os.path.exists(db_path):
        print(f"Удаление существующей базы данных: {db_path}")
        os.remove(db_path)

    # Создаем новую БД и инициализируем схему
    print("Создание новой базы данных...")
    db = DatabaseConnection(db_path)

    try:
        db.initialize_db(schema_path)
        print("База данных успешно инициализирована")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    init_database()