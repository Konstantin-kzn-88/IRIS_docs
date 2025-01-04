# database/repositories/organization_repo.py
from typing import List, Optional
from models.organization import Organization
from ..db_connection import DatabaseConnection


class OrganizationRepository:
    """Репозиторий для работы с организациями"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create(self, organization: Organization) -> Organization:
        """Создание новой организации"""
        query = """
            INSERT INTO organizations (
                name, full_name, org_form, head_position, head_name,
                legal_address, phone, fax, email, license_number,
                license_date, ind_safety_system, prod_control,
                accident_investigation, rescue_contract,
                rescue_certificate, fire_contract,
                emergency_certificate, material_reserves,
                financial_reserves
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Конвертируем дату в строку ISO формата если она есть
        license_date = (organization.license_date.isoformat()
                        if organization.license_date else None)

        params = (
            organization.name, organization.full_name,
            organization.org_form, organization.head_position,
            organization.head_name, organization.legal_address,
            organization.phone, organization.fax,
            organization.email, organization.license_number,
            license_date, organization.ind_safety_system,
            organization.prod_control, organization.accident_investigation,
            organization.rescue_contract, organization.rescue_certificate,
            organization.fire_contract, organization.emergency_certificate,
            organization.material_reserves, organization.financial_reserves
        )

        # Выполняем запрос и получаем id
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            organization.id = cursor.lastrowid

        return organization

    def get_by_id(self, org_id: int) -> Optional[Organization]:
        """Получение организации по id"""
        query = "SELECT * FROM organizations WHERE id = ?"
        result = self.db.execute_query(query, (org_id,))

        if result:
            return Organization.from_dict(dict(result[0]))
        return None

    def get_all(self) -> List[Organization]:
        """Получение всех организаций"""
        query = "SELECT * FROM organizations ORDER BY name"
        result = self.db.execute_query(query)
        return [Organization.from_dict(dict(row)) for row in result]

    def update(self, organization: Organization) -> Organization:
        """Обновление организации"""
        query = """
            UPDATE organizations SET
                name = ?, full_name = ?, org_form = ?,
                head_position = ?, head_name = ?,
                legal_address = ?, phone = ?, fax = ?,
                email = ?, license_number = ?,
                license_date = ?, ind_safety_system = ?,
                prod_control = ?, accident_investigation = ?,
                rescue_contract = ?, rescue_certificate = ?,
                fire_contract = ?, emergency_certificate = ?,
                material_reserves = ?, financial_reserves = ?
            WHERE id = ?
        """

        # Конвертируем дату в строку ISO формата если она есть
        license_date = (organization.license_date.isoformat()
                        if organization.license_date else None)

        params = (
            organization.name, organization.full_name,
            organization.org_form, organization.head_position,
            organization.head_name, organization.legal_address,
            organization.phone, organization.fax,
            organization.email, organization.license_number,
            license_date, organization.ind_safety_system,
            organization.prod_control, organization.accident_investigation,
            organization.rescue_contract, organization.rescue_certificate,
            organization.fire_contract, organization.emergency_certificate,
            organization.material_reserves, organization.financial_reserves,
            organization.id
        )

        self.db.execute_query(query, params)
        return organization

    def delete(self, org_id: int) -> bool:
        """Удаление организации"""
        query = "DELETE FROM organizations WHERE id = ?"
        self.db.execute_query(query, (org_id,))
        return True

    def search(self, search_term: str) -> List[Organization]:
        """Поиск организаций по названию или полному названию"""
        query = """
            SELECT * FROM organizations 
            WHERE name LIKE ? OR full_name LIKE ? 
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        result = self.db.execute_query(query, (search_pattern, search_pattern))
        return [Organization.from_dict(dict(row)) for row in result]

    def get_by_org_form(self, org_form: str) -> List[Organization]:
        """Получение организаций по форме собственности"""
        query = "SELECT * FROM organizations WHERE org_form = ? ORDER BY name"
        result = self.db.execute_query(query, (org_form,))
        return [Organization.from_dict(dict(row)) for row in result]


# Пример использования:
if __name__ == "__main__":
    from datetime import date

    # Создаем подключение к БД
    db = DatabaseConnection("industrial_safety.db")

    # Создаем репозиторий
    repo = OrganizationRepository(db)

    # Создаем тестовую организацию
    org = Organization(
        id=None,
        name="ООО Тест",
        full_name="Общество с ограниченной ответственностью Тест",
        org_form="ООО",
        head_position="Генеральный директор",
        head_name="Иванов И.И.",
        legal_address="г. Москва, ул. Тестовая, д. 1",
        phone="+7 (999) 123-45-67",
        fax=None,
        email="test@example.com",
        license_number="12345",
        license_date=date(2024, 1, 1),
        ind_safety_system="Есть",
        prod_control="Есть",
        accident_investigation="Есть",
        rescue_contract="Есть",
        rescue_certificate="123",
        fire_contract="Есть",
        emergency_certificate="456",
        material_reserves="Есть",
        financial_reserves="Есть"
    )

    try:
        # Создаем организацию
        created_org = repo.create(org)
        print(f"Создана организация с id: {created_org.id}")

        # Получаем все организации
        all_orgs = repo.get_all()
        print(f"Всего организаций: {len(all_orgs)}")

    finally:
        db.close()