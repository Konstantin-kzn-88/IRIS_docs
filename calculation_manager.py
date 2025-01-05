# calculation_manager.py

from typing import List
from database.db_connection import DatabaseConnection
from models.equipment import (
    BaseEquipment, EquipmentType, Pipeline, Pump,
    TechnologicalDevice, Tank, TruckTank, Compressor
)
from models.calculation_result import CalculationResult
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository


class CalculationManager:
    """Менеджер для управления расчетами"""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.equipment_repo = EquipmentRepository(db)
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)

    def get_project_equipment(self, project_id: int) -> List[BaseEquipment]:
        """Получение всего оборудования для проекта"""
        all_equipment = []

        # Получаем оборудование каждого типа
        equipment_types = [
            EquipmentType.PIPELINE,
            EquipmentType.PUMP,
            EquipmentType.TECHNOLOGICAL_DEVICE,
            EquipmentType.TANK,
            EquipmentType.TRUCK_TANK,
            EquipmentType.COMPRESSOR
        ]

        for eq_type in equipment_types:
            equipment = self.equipment_repo.get_by_type(eq_type)
            # Фильтруем по проекту
            project_equipment = [eq for eq in equipment if eq.project_id == project_id]
            all_equipment.extend(project_equipment)

        return all_equipment

    def create_initial_calculation(self, project_code: str) -> None:
        """Создание начального расчета для проекта"""
        # Сначала очищаем старые расчеты для этого проекта
        self.clear_project_calculations(project_code)

        # Получаем проект
        project = next((p for p in self.project_repo.get_all()
                        if p.project_code == project_code), None)
        if not project:
            raise ValueError(f"Проект с кодом {project_code} не найден")

        # Получаем оборудование проекта
        equipment = self.get_project_equipment(project.id)
        if not equipment:
            raise ValueError(f"Для проекта {project_code} не найдено оборудование")

        # Берем первое оборудование для начального расчета
        eq = equipment[0]

        # Получаем вещество
        substance = self.substance_repo.get_by_id(eq.substance_id)
        if not substance:
            raise ValueError(f"Вещество не найдено для оборудования {eq.name}")

        # Создаем запись расчета
        calculation = CalculationResult(
            id=None,
            project_code=project_code,
            scenario_number=1,  # С1
            equipment_name=eq.name,
            equipment_type=eq.equipment_type,
            substance_type=substance.sub_type,
            q_10_5=0.0,
            q_7_0=0.0,
            q_4_2=0.0,
            q_1_4=0.0,
            p_53=0.0,
            p_28=0.0,
            p_12=0.0,
            p_5=0.0,
            p_2=0.0,
            l_f=0.0,
            d_f=0.0,
            r_nkpr=0.0,
            r_flash=0.0,
            l_pt=0.0,
            p_pt=0.0,
            q_600=0.0,
            q_320=0.0,
            q_220=0.0,
            q_120=0.0,
            s_spill=0.0,
            casualties=0,
            injured=0,
            direct_losses=0.0,
            liquidation_costs=0.0,
            social_losses=0.0,
            indirect_damage=0.0,
            environmental_damage=0.0,
            total_damage=0.0,
            casualty_risk=0.0,
            injury_risk=0.0,
            expected_damage=0.0
        )

        # Сохраняем в БД
        self._save_calculation(calculation)

    def clear_project_calculations(self, project_code: str) -> None:
        """Очистка всех расчетов для проекта"""
        query = "DELETE FROM calculation_results WHERE project_code = ?"
        self.db.execute_query(query, (project_code,))

    def _save_calculation(self, calculation: CalculationResult) -> None:
        """Сохранение расчета в БД"""
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
                casualty_risk, injury_risk, expected_damage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            calculation.project_code,
            calculation.scenario_number,
            calculation.equipment_name,
            calculation.equipment_type.value,
            int(calculation.substance_type),
            calculation.q_10_5,
            calculation.q_7_0,
            calculation.q_4_2,
            calculation.q_1_4,
            calculation.p_53,
            calculation.p_28,
            calculation.p_12,
            calculation.p_5,
            calculation.p_2,
            calculation.l_f,
            calculation.d_f,
            calculation.r_nkpr,
            calculation.r_flash,
            calculation.l_pt,
            calculation.p_pt,
            calculation.q_600,
            calculation.q_320,
            calculation.q_220,
            calculation.q_120,
            calculation.s_spill,
            calculation.casualties,
            calculation.injured,
            calculation.direct_losses,
            calculation.liquidation_costs,
            calculation.social_losses,
            calculation.indirect_damage,
            calculation.environmental_damage,
            calculation.total_damage,
            calculation.casualty_risk,
            calculation.injury_risk,
            calculation.expected_damage
        )

        self.db.execute_query(query, params)