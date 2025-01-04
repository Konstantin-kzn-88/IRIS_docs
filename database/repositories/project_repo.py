# database/repositories/project_repo.py
from typing import List, Optional
from models.project import Project
from ..db_connection import DatabaseConnection


class ProjectRepository:
    """Репозиторий для работы с проектами"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create(self, project: Project) -> Project:
        """Создание нового проекта"""
        query = """
            INSERT INTO projects (
                opo_id, name, description, automation_description,
                project_code, dpb_code, rpz_code, ifl_code,
                gochs_code, mpb_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            project.opo_id,
            project.name,
            project.description,
            project.automation_description,
            project.project_code,
            project.dpb_code,
            project.rpz_code,
            project.ifl_code,
            project.gochs_code,
            project.mpb_code
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            project.id = cursor.lastrowid

        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Получение проекта по id"""
        query = "SELECT * FROM projects WHERE id = ?"
        result = self.db.execute_query(query, (project_id,))

        if result:
            return Project.from_dict(dict(result[0]))
        return None

    def get_by_opo(self, opo_id: int) -> List[Project]:
        """Получение всех проектов ОПО"""
        query = """
            SELECT * FROM projects 
            WHERE opo_id = ?
            ORDER BY name
        """
        result = self.db.execute_query(query, (opo_id,))
        return [Project.from_dict(dict(row)) for row in result]

    def get_all(self) -> List[Project]:
        """Получение всех проектов"""
        query = "SELECT * FROM projects ORDER BY name"
        result = self.db.execute_query(query)
        return [Project.from_dict(dict(row)) for row in result]

    def update(self, project: Project) -> Project:
        """Обновление проекта"""
        query = """
            UPDATE projects SET
                opo_id = ?,
                name = ?,
                description = ?,
                automation_description = ?,
                project_code = ?,
                dpb_code = ?,
                rpz_code = ?,
                ifl_code = ?,
                gochs_code = ?,
                mpb_code = ?
            WHERE id = ?
        """
        params = (
            project.opo_id,
            project.name,
            project.description,
            project.automation_description,
            project.project_code,
            project.dpb_code,
            project.rpz_code,
            project.ifl_code,
            project.gochs_code,
            project.mpb_code,
            project.id
        )

        self.db.execute_query(query, params)
        return project

    def delete(self, project_id: int) -> bool:
        """Удаление проекта"""
        query = "DELETE FROM projects WHERE id = ?"
        self.db.execute_query(query, (project_id,))
        return True

    def search(self, search_term: str) -> List[Project]:
        """Поиск проектов по названию или кодам"""
        query = """
            SELECT * FROM projects 
            WHERE name LIKE ? 
               OR project_code LIKE ?
               OR dpb_code LIKE ?
               OR rpz_code LIKE ?
               OR ifl_code LIKE ?
               OR gochs_code LIKE ?
               OR mpb_code LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern,) * 7  # Повторяем паттерн для каждого поля

        result = self.db.execute_query(query, params)
        return [Project.from_dict(dict(row)) for row in result]

    def get_by_code(self, code_type: str, code_value: str) -> List[Project]:
        """Получение проектов по определенному коду"""
        if code_type not in ['project_code', 'dpb_code', 'rpz_code',
                             'ifl_code', 'gochs_code', 'mpb_code']:
            raise ValueError("Неверный тип кода")

        query = f"""
            SELECT * FROM projects 
            WHERE {code_type} = ?
            ORDER BY name
        """
        result = self.db.execute_query(query, (code_value,))
        return [Project.from_dict(dict(row)) for row in result]


# Пример использования:
if __name__ == "__main__":
    db = DatabaseConnection("industrial_safety.db")
    repo = ProjectRepository(db)

    try:
        # Создаем тестовый проект
        project = Project(
            id=None,
            opo_id=1,  # ID существующего ОПО
            name="Тестовый проект",
            description="Описание тестового проекта",
            automation_description="Описание автоматизации",
            project_code="TP-2024-001",
            dpb_code="DPB-001",
            rpz_code="RPZ-001",
            ifl_code="IFL-001",
            gochs_code="GOCHS-001",
            mpb_code="MPB-001"
        )

        # Сохраняем в БД
        created_project = repo.create(project)
        print(f"Создан проект с id: {created_project.id}")

        # Ищем проекты по коду ДПБ
        dpb_projects = repo.get_by_code('dpb_code', 'DPB-001')
        print(f"Найдено проектов с кодом DPB-001: {len(dpb_projects)}")

    finally:
        db.close()
        