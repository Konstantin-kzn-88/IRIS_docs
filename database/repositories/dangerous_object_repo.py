# database/repositories/dangerous_object_repo.py
from typing import List, Optional
from models.dangerous_object import DangerousObject, HazardClass
from ..db_connection import DatabaseConnection


class DangerousObjectRepository:
    """Репозиторий для работы с опасными производственными объектами"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create(self, obj: DangerousObject) -> DangerousObject:
        """Создание нового ОПО"""
        query = """
            INSERT INTO dangerous_objects (
                organization_id, name, reg_number,
                hazard_class, location, employee_count
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            obj.organization_id,
            obj.name,
            obj.reg_number,
            obj.hazard_class.value,  # Преобразуем enum в строку
            obj.location,
            obj.employee_count
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            obj.id = cursor.lastrowid

        return obj

    def get_by_id(self, obj_id: int) -> Optional[DangerousObject]:
        """Получение ОПО по id"""
        query = "SELECT * FROM dangerous_objects WHERE id = ?"
        result = self.db.execute_query(query, (obj_id,))

        if result:
            return DangerousObject.from_dict(dict(result[0]))
        return None

    def get_by_organization(self, organization_id: int) -> List[DangerousObject]:
        """Получение всех ОПО организации"""
        query = """
            SELECT * FROM dangerous_objects 
            WHERE organization_id = ?
            ORDER BY name
        """
        result = self.db.execute_query(query, (organization_id,))
        return [DangerousObject.from_dict(dict(row)) for row in result]

    def get_all(self) -> List[DangerousObject]:
        """Получение всех ОПО"""
        query = "SELECT * FROM dangerous_objects ORDER BY name"
        result = self.db.execute_query(query)
        return [DangerousObject.from_dict(dict(row)) for row in result]

    def update(self, obj: DangerousObject) -> DangerousObject:
        """Обновление ОПО"""
        query = """
            UPDATE dangerous_objects SET
                organization_id = ?,
                name = ?,
                reg_number = ?,
                hazard_class = ?,
                location = ?,
                employee_count = ?
            WHERE id = ?
        """
        params = (
            obj.organization_id,
            obj.name,
            obj.reg_number,
            obj.hazard_class.value,
            obj.location,
            obj.employee_count,
            obj.id
        )

        self.db.execute_query(query, params)
        return obj

    def delete(self, obj_id: int) -> bool:
        """Удаление ОПО"""
        query = "DELETE FROM dangerous_objects WHERE id = ?"
        self.db.execute_query(query, (obj_id,))
        return True

    def search(self, search_term: str) -> List[DangerousObject]:
        """Поиск ОПО по названию или рег. номеру"""
        query = """
            SELECT * FROM dangerous_objects 
            WHERE name LIKE ? OR reg_number LIKE ? 
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        result = self.db.execute_query(query, (search_pattern, search_pattern))
        return [DangerousObject.from_dict(dict(row)) for row in result]

    def get_by_hazard_class(self, hazard_class: HazardClass) -> List[DangerousObject]:
        """Получение ОПО по классу опасности"""
        query = """
            SELECT * FROM dangerous_objects 
            WHERE hazard_class = ? 
            ORDER BY name
        """
        result = self.db.execute_query(query, (hazard_class.value,))
        return [DangerousObject.from_dict(dict(row)) for row in result]


# Пример использования:
if __name__ == "__main__":
    db = DatabaseConnection("industrial_safety.db")
    repo = DangerousObjectRepository(db)

    try:
        # Создаем тестовый ОПО
        obj = DangerousObject(
            id=None,
            organization_id=1,  # ID существующей организации
            name="Тестовый ОПО",
            reg_number="А-01-12345-2024",
            hazard_class=HazardClass.CLASS_II,
            location="г. Москва, ул. Тестовая, д. 1",
            employee_count=100
        )

        # Сохраняем в БД
        created_obj = repo.create(obj)
        print(f"Создан ОПО с id: {created_obj.id}")

        # Получаем все ОПО II класса опасности
        class_2_objects = repo.get_by_hazard_class(HazardClass.CLASS_II)
        print(f"ОПО II класса опасности: {len(class_2_objects)}")

    finally:
        db.close()