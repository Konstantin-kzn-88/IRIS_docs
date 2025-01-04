# database/repositories/substance_repo.py
from typing import List, Optional
from models.substance import Substance, SubstanceType
from ..db_connection import DatabaseConnection


class SubstanceRepository:
    """Репозиторий для работы с веществами"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create(self, substance: Substance) -> Substance:
        """Создание нового вещества"""
        query = """
            INSERT INTO substances (
                sub_name, class_substance, sub_type,
                density_liquid, molecular_weight,
                boiling_temperature_liquid,
                heat_evaporation_liquid, adiabatic,
                heat_capacity_liquid, heat_of_combustion,
                sigma, energy_level, flash_point,
                auto_ignition_temp, lower_concentration_limit,
                upper_concentration_limit, threshold_toxic_dose,
                lethal_toxic_dose
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            substance.sub_name,
            substance.class_substance,
            int(substance.sub_type),  # преобразуем enum в int
            substance.density_liquid,
            substance.molecular_weight,
            substance.boiling_temperature_liquid,
            substance.heat_evaporation_liquid,
            substance.adiabatic,
            substance.heat_capacity_liquid,
            substance.heat_of_combustion,
            substance.sigma,
            substance.energy_level,
            substance.flash_point,
            substance.auto_ignition_temp,
            substance.lower_concentration_limit,
            substance.upper_concentration_limit,
            substance.threshold_toxic_dose,
            substance.lethal_toxic_dose
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            substance.id = cursor.lastrowid

        return substance

    def get_by_id(self, substance_id: int) -> Optional[Substance]:
        """Получение вещества по id"""
        query = "SELECT * FROM substances WHERE id = ?"
        result = self.db.execute_query(query, (substance_id,))

        if result:
            return Substance.from_dict(dict(result[0]))
        return None

    def get_all(self) -> List[Substance]:
        """Получение всех веществ"""
        query = "SELECT * FROM substances ORDER BY sub_name"
        result = self.db.execute_query(query)
        return [Substance.from_dict(dict(row)) for row in result]

    def update(self, substance: Substance) -> Substance:
        """Обновление вещества"""
        query = """
            UPDATE substances SET
                sub_name = ?,
                class_substance = ?,
                sub_type = ?,
                density_liquid = ?,
                molecular_weight = ?,
                boiling_temperature_liquid = ?,
                heat_evaporation_liquid = ?,
                adiabatic = ?,
                heat_capacity_liquid = ?,
                heat_of_combustion = ?,
                sigma = ?,
                energy_level = ?,
                flash_point = ?,
                auto_ignition_temp = ?,
                lower_concentration_limit = ?,
                upper_concentration_limit = ?,
                threshold_toxic_dose = ?,
                lethal_toxic_dose = ?
            WHERE id = ?
        """
        params = (
            substance.sub_name,
            substance.class_substance,
            int(substance.sub_type),
            substance.density_liquid,
            substance.molecular_weight,
            substance.boiling_temperature_liquid,
            substance.heat_evaporation_liquid,
            substance.adiabatic,
            substance.heat_capacity_liquid,
            substance.heat_of_combustion,
            substance.sigma,
            substance.energy_level,
            substance.flash_point,
            substance.auto_ignition_temp,
            substance.lower_concentration_limit,
            substance.upper_concentration_limit,
            substance.threshold_toxic_dose,
            substance.lethal_toxic_dose,
            substance.id
        )

        self.db.execute_query(query, params)
        return substance

    def delete(self, substance_id: int) -> bool:
        """Удаление вещества"""
        query = "DELETE FROM substances WHERE id = ?"
        self.db.execute_query(query, (substance_id,))
        return True

    def search(self, search_term: str) -> List[Substance]:
        """Поиск веществ по названию"""
        query = """
            SELECT * FROM substances 
            WHERE sub_name LIKE ? 
            ORDER BY sub_name
        """
        search_pattern = f"%{search_term}%"
        result = self.db.execute_query(query, (search_pattern,))
        return [Substance.from_dict(dict(row)) for row in result]

    def get_by_class(self, class_substance: int) -> List[Substance]:
        """Получение веществ по классу опасности"""
        query = """
            SELECT * FROM substances 
            WHERE class_substance = ? 
            ORDER BY sub_name
        """
        result = self.db.execute_query(query, (class_substance,))
        return [Substance.from_dict(dict(row)) for row in result]

    def get_by_type(self, sub_type: SubstanceType) -> List[Substance]:
        """Получение веществ по типу"""
        query = """
            SELECT * FROM substances 
            WHERE sub_type = ? 
            ORDER BY sub_name
        """
        result = self.db.execute_query(query, (int(sub_type),))
        return [Substance.from_dict(dict(row)) for row in result]


# Пример использования:
if __name__ == "__main__":
    db = DatabaseConnection("industrial_safety.db")
    repo = SubstanceRepository(db)

    try:
        # Создаем тестовое вещество
        substance = Substance(
            id=None,
            sub_name="Тестовое вещество",
            class_substance=2,
            sub_type=SubstanceType.LVJ,
            density_liquid=800.0,
            molecular_weight=100.0,
            boiling_temperature_liquid=80.0,
            heat_evaporation_liquid=250.0,
            adiabatic=1.4,
            heat_capacity_liquid=2.1,
            heat_of_combustion=46000.0,
            sigma=4,
            energy_level=1,
            flash_point=25.0,
            auto_ignition_temp=450.0,
            lower_concentration_limit=1.5,
            upper_concentration_limit=7.5,
            threshold_toxic_dose=None,
            lethal_toxic_dose=None
        )

        # Сохраняем в БД
        created_substance = repo.create(substance)
        print(f"Создано вещество с id: {created_substance.id}")

        # Получаем все ЛВЖ
        lvj_substances = repo.get_by_type(SubstanceType.LVJ)
        print(f"Найдено ЛВЖ: {len(lvj_substances)}")

    finally:
        db.close()