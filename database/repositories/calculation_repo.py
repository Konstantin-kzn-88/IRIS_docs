# database/repositories/calculation_repo.py
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from models.calculation_result import CalculationResult
from models.equipment import EquipmentType
from models.substance import SubstanceType
from ..db_connection import DatabaseConnection


class CalculationResultRepository:
    """Репозиторий для работы с результатами расчетов"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def create(self, result: CalculationResult) -> CalculationResult:
        """Создание нового результата расчета"""
        query = """
            INSERT INTO calculation_results (
                project_code, scenario_number, equipment_name,
                equipment_type, substance_type,
                q_10_5, q_7_0, q_4_2, q_1_4,
                p_53, p_28, p_12, p_5, p_2,
                l_f, d_f, r_nkpr, r_flash, l_pt, p_pt,
                q_600, q_320, q_220, q_120,
                s_spill, casualties, injured,
                direct_losses, liquidation_costs,
                social_losses, indirect_damage,
                environmental_damage, total_damage,
                casualty_risk, injury_risk, expected_damage,
                probability                          # Добавляем поле
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?)                              # Добавляем параметр
        """

        params = (
            result.project_code,
            result.scenario_number,
            result.equipment_name,
            result.equipment_type.value,
            int(result.substance_type),
            result.q_10_5,
            result.q_7_0,
            result.q_4_2,
            result.q_1_4,
            result.p_53,
            result.p_28,
            result.p_12,
            result.p_5,
            result.p_2,
            result.l_f,
            result.d_f,
            result.r_nkpr,
            result.r_flash,
            result.l_pt,
            result.p_pt,
            result.q_600,
            result.q_320,
            result.q_220,
            result.q_120,
            result.s_spill,
            result.casualties,
            result.injured,
            result.direct_losses,
            result.liquidation_costs,
            result.social_losses,
            result.indirect_damage,
            result.environmental_damage,
            result.total_damage,
            result.casualty_risk,
            result.injury_risk,
            result.expected_damage,
            result.probability  # Добавляем параметр
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            result.id = cursor.lastrowid

        return result

    def get_all(self) -> List[CalculationResult]:
        """Получение всех результатов расчетов"""
        query = "SELECT * FROM calculation_results ORDER BY project_code, scenario_number"
        result = self.db.execute_query(query)
        return [CalculationResult.from_dict(dict(row)) for row in result]

    def get_by_id(self, result_id: int) -> Optional[CalculationResult]:
        """Получение результата расчета по id"""
        query = "SELECT * FROM calculation_results WHERE id = ?"
        result = self.db.execute_query(query, (result_id,))

        if result:
            return CalculationResult.from_dict(dict(result[0]))
        return None

    def get_by_project(self, project_code: str) -> List[CalculationResult]:
        """Получение всех результатов расчетов для проекта"""
        query = """
            SELECT * FROM calculation_results 
            WHERE project_code = ?
            ORDER BY scenario_number
        """
        result = self.db.execute_query(query, (project_code,))
        return [CalculationResult.from_dict(dict(row)) for row in result]

    def get_by_scenario(self, project_code: str, scenario_number: int) -> List[CalculationResult]:
        """Получение результатов расчета для конкретного сценария"""
        query = """
            SELECT * FROM calculation_results 
            WHERE project_code = ? AND scenario_number = ?
        """
        results = self.db.execute_query(query, (project_code, scenario_number))
        return [CalculationResult.from_dict(dict(row)) for row in results]

    def get_risk_metrics(self, project_code: str) -> Dict[str, Any]:
        """Получение агрегированных метрик риска для проекта"""
        query = """
            SELECT 
                MAX(casualties) as max_casualties,
                MAX(injured) as max_injured,
                AVG(casualties) as avg_casualties,
                AVG(injured) as avg_injured,
                MAX(total_damage) as max_damage,
                AVG(total_damage) as avg_damage,
                MAX(casualty_risk) as max_casualty_risk,
                MAX(injury_risk) as max_injury_risk
            FROM calculation_results 
            WHERE project_code = ?
        """
        result = self.db.execute_query(query, (project_code,))
        if result:
            return dict(result[0])
        return {}

    def get_damage_summary(self, project_code: str) -> Dict[str, Decimal]:
        """Получение суммарного ущерба по типам для проекта"""
        query = """
            SELECT 
                SUM(direct_losses) as total_direct,
                SUM(liquidation_costs) as total_liquidation,
                SUM(social_losses) as total_social,
                SUM(indirect_damage) as total_indirect,
                SUM(environmental_damage) as total_environmental,
                SUM(total_damage) as grand_total
            FROM calculation_results 
            WHERE project_code = ?
        """
        result = self.db.execute_query(query, (project_code,))
        if result:
            return dict(result[0])
        return {}

    def get_high_risk_scenarios(self, casualties_threshold: int = 1) -> List[Tuple[str, int]]:
        """Получение сценариев с высоким риском"""
        query = """
            SELECT project_code, scenario_number
            FROM calculation_results 
            WHERE casualties >= ?
            ORDER BY casualties DESC
        """
        results = self.db.execute_query(query, (casualties_threshold,))
        return [(row['project_code'], row['scenario_number']) for row in results]

    def get_by_equipment_type(self, equipment_type: EquipmentType) -> List[CalculationResult]:
        """Получение результатов расчетов для определенного типа оборудования"""
        query = """
            SELECT * FROM calculation_results 
            WHERE equipment_type = ?
            ORDER BY casualties DESC
        """
        results = self.db.execute_query(query, (equipment_type.value,))
        return [CalculationResult.from_dict(dict(row)) for row in results]

    def get_by_substance_type(self, substance_type: SubstanceType) -> List[CalculationResult]:
        """Получение результатов расчетов для определенного типа вещества"""
        query = """
            SELECT * FROM calculation_results 
            WHERE substance_type = ?
            ORDER BY casualties DESC
        """
        results = self.db.execute_query(query, (int(substance_type),))
        return [CalculationResult.from_dict(dict(row)) for row in results]

    def update(self, result: CalculationResult) -> CalculationResult:
        """Обновление результата расчета"""
        query = """
            UPDATE calculation_results SET
                project_code = ?, scenario_number = ?,
                equipment_name = ?, equipment_type = ?,
                substance_type = ?, q_10_5 = ?, q_7_0 = ?,
                q_4_2 = ?, q_1_4 = ?, p_53 = ?, p_28 = ?,
                p_12 = ?, p_5 = ?, p_2 = ?, l_f = ?,
                d_f = ?, r_nkpr = ?, r_flash = ?, l_pt = ?,
                p_pt = ?, q_600 = ?, q_320 = ?, q_220 = ?,
                q_120 = ?, s_spill = ?, casualties = ?,
                injured = ?, direct_losses = ?,
                liquidation_costs = ?, social_losses = ?,
                indirect_damage = ?, environmental_damage = ?,
                total_damage = ?, casualty_risk = ?,
                injury_risk = ?, expected_damage = ?, probability = ?
            WHERE id = ?
        """
        params = (
            result.project_code, result.scenario_number,
            result.equipment_name, result.equipment_type.value,
            int(result.substance_type), result.q_10_5,
            result.q_7_0, result.q_4_2, result.q_1_4,
            result.p_53, result.p_28, result.p_12,
            result.p_5, result.p_2, result.l_f,
            result.d_f, result.r_nkpr, result.r_flash,
            result.l_pt, result.p_pt, result.q_600,
            result.q_320, result.q_220, result.q_120,
            result.s_spill, result.casualties,
            result.injured, result.direct_losses,
            result.liquidation_costs, result.social_losses,
            result.indirect_damage, result.environmental_damage,
            result.total_damage, result.casualty_risk,
            result.injury_risk, result.expected_damage,
            result.probability,
            result.id
        )

        self.db.execute_query(query, params)
        return result

    def delete(self, result_id: int) -> bool:
        """Удаление результата расчета"""
        query = "DELETE FROM calculation_results WHERE id = ?"
        self.db.execute_query(query, (result_id,))
        return True

    def delete_by_project(self, project_code: str) -> bool:
        """Удаление всех результатов расчета для проекта"""
        query = "DELETE FROM calculation_results WHERE project_code = ?"
        self.db.execute_query(query, (project_code,))
        return True

    def get_project_summary(self, project_code: str) -> dict:
        """Получение сводной информации по проекту"""
        query = """
            SELECT 
                COUNT(*) as scenario_count,
                SUM(casualties) as total_casualties,
                SUM(injured) as total_injured,
                MAX(total_damage) as max_damage,
                AVG(total_damage) as avg_damage,
                SUM(total_damage) as sum_damage
            FROM calculation_results 
            WHERE project_code = ?
        """
        result = self.db.execute_query(query, (project_code,))
        if result:
            return dict(result[0])
        return {}


# Пример использования:
if __name__ == "__main__":
    db = DatabaseConnection("industrial_safety.db")
    repo = CalculationResultRepository(db)

    try:
        # Создаем тестовый результат расчета
        result = CalculationResult(
            id=None,
            project_code="TP-2024-001",
            scenario_number=1,
            equipment_name="Тестовый трубопровод",
            equipment_type=EquipmentType.PIPELINE,
            substance_type=SubstanceType.LVJ,
            q_10_5=100.0,
            q_7_0=150.0,
            q_4_2=200.0,
            q_1_4=300.0,
            p_53=10.0,
            p_28=20.0,
            p_12=30.0,
            p_5=40.0,
            p_2=50.0,
            l_f=15.0,
            d_f=2.0,
            r_nkpr=25.0,
            r_flash=30.0,
            l_pt=45.0,
            p_pt=10.0,
            q_600=5.0,
            q_320=10.0,
            q_220=15.0,
            q_120=20.0,
            s_spill=100.0,
            casualties=2,
            injured=5,
            direct_losses=1.5,
            liquidation_costs=0.5,
            social_losses=1.0,
            indirect_damage=0.8,
            environmental_damage=0.2,
            total_damage=4.0,
            casualty_risk=0.0001,
            injury_risk=0.0005,
            expected_damage=0.004,
            probability=1e-6  # Добавляем новое поле
        )

        # Сохраняем в БД
        created_result = repo.create(result)
        print(f"Создан результат расчета с id: {created_result.id}")

        # Получаем метрики риска
        risk_metrics = repo.get_risk_metrics("TP-2024-001")
        print("Метрики риска:", risk_metrics)

        # Получаем суммарный ущерб
        damage_summary = repo.get_damage_summary("TP-2024-001")
        print("Суммарный ущерб:", damage_summary)

    finally:
        db.close()