# database/db_connection.py
import sqlite3
from sqlite3 import Error
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager
import logging
import os


class DatabaseConnection:
    """Класс для работы с SQLite базой данных"""

    def __init__(self, db_path: str):
        """
        Инициализация подключения к БД

        Args:
            db_path: путь к файлу базы данных
        """
        self.db_path = db_path
        self._connection = None
        self.setup_logging()

    def setup_logging(self) -> None:
        """Настройка логирования"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @contextmanager
    def get_connection(self) -> sqlite3.Connection:
        """
        Контекстный менеджер для получения соединения с БД

        Returns:
            sqlite3.Connection: объект соединения с БД
        """
        try:
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row

            # Включаем поддержку foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")

            yield self._connection

        except Error as e:
            self.logger.error(f"Ошибка при подключении к БД: {e}")
            raise

    @contextmanager
    def get_cursor(self) -> sqlite3.Cursor:
        """
        Контекстный менеджер для получения курсора БД

        Returns:
            sqlite3.Cursor: объект курсора БД
        """
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                yield cursor
                connection.commit()

            except Error as e:
                connection.rollback()
                self.logger.error(f"Ошибка при работе с БД: {e}")
                raise

            finally:
                cursor.close()

    def execute_query(self, query: str, parameters: Tuple[Any, ...] = ()) -> Optional[List[sqlite3.Row]]:
        """
        Выполнение SQL запроса

        Args:
            query: SQL запрос
            parameters: параметры запроса

        Returns:
            Optional[List[sqlite3.Row]]: результат запроса или None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, parameters)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                return None

        except Error as e:
            self.logger.error(f"Ошибка при выполнении запроса: {e}\nЗапрос: {query}\nПараметры: {parameters}")
            raise

    def execute_many(self, query: str, parameters: List[Tuple[Any, ...]]) -> None:
        """
        Выполнение множества SQL запросов

        Args:
            query: SQL запрос
            parameters: список параметров для каждого запроса
        """
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, parameters)

        except Error as e:
            self.logger.error(f"Ошибка при выполнении множества запросов: {e}\nЗапрос: {query}")
            raise

    def initialize_db(self, schema_path: str) -> None:
        """
        Инициализация базы данных из SQL файла

        Args:
            schema_path: путь к файлу со схемой БД
        """
        try:
            # Проверяем существование файла схемы
            if not os.path.exists(schema_path):
                raise FileNotFoundError(f"Файл схемы не найден: {schema_path}")

            # Читаем SQL скрипт
            with open(schema_path, 'r', encoding='utf-8') as file:
                schema_script = file.read()

            # Выполняем скрипт
            with self.get_connection() as connection:
                connection.executescript(schema_script)
                self.logger.info("База данных успешно инициализирована")

        except Error as e:
            self.logger.error(f"Ошибка при инициализации БД: {e}")
            raise

        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при инициализации БД: {e}")
            raise

    def close(self) -> None:
        """Закрытие соединения с БД"""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                self.logger.debug("Соединение с БД закрыто")

            except Error as e:
                self.logger.error(f"Ошибка при закрытии соединения с БД: {e}")
                raise


# Пример использования
if __name__ == "__main__":
    # Создаем подключение к БД
    db = DatabaseConnection("industrial_safety.db")

    try:
        # Инициализируем БД из схемы
        db.initialize_db("schema.sql")

        # Пример запроса
        result = db.execute_query("SELECT * FROM organizations LIMIT 1")
        if result:
            org = result[0]
            print(f"Первая организация: {dict(org)}")

    finally:
        # Закрываем соединение
        db.close()