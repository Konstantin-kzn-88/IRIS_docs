# calculation_manager.py

from typing import List
from database.db_connection import DatabaseConnection
from models.dangerous_object import DangerousObject
from models.equipment import (
    BaseEquipment, EquipmentType, Pipeline, Pump,
    TechnologicalDevice, Tank, TruckTank, Compressor
)
from models.calculation_result import CalculationResult
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from calc_method import calc_pipe_0, calc_tank_0, calc_truc_tank_0, calc_device_0, calc_pump_0, calc_pipe_1, \
    calc_device_1


class CalculationManager:
    """Менеджер для управления расчетами"""

    def __init__(self, db: DatabaseConnection, main_window=None):
        self.db = db
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.equipment_repo = EquipmentRepository(db)
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)

    def get_main_window(self):
        """Получение ссылки на главное окно"""
        return self.main_window

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
        self.clear_project_calculations()

        # Получаем проект
        project = next((p for p in self.project_repo.get_all()
                        if p.project_code == project_code), None)
        if not project:
            raise ValueError(f"Проект с кодом {project_code} не найден")

        # Получаем ОПО для проекта
        dangerous_object = self.db.execute_query(
            "SELECT * FROM dangerous_objects WHERE id = ?",
            (project.opo_id,)
        )
        if not dangerous_object:
            raise ValueError(f"ОПО для проекта {project_code} не найден")

        # Преобразуем результат запроса в объект
        dangerous_object = DangerousObject.from_dict(dict(dangerous_object[0]))

        # Получаем оборудование проекта
        equipments = self.get_project_equipment(project.id)
        if not equipments:
            raise ValueError(f"Для проекта {project_code} не найдено оборудование")

        # Генерация расчетов
        init_num_scenario = 1

        for equipment in equipments:

            # Получаем вещество
            substance = self.substance_repo.get_by_id(equipment.substance_id)
            if not substance:
                raise ValueError(f"Вещество не найдено для оборудования {equipment.name}")

            # print(type(equipment.equipment_type.value), substance.sub_type.value)
            if equipment.equipment_type.value == 'Pipeline':
                if substance.sub_type.value == 0:  # ЛВЖ
                    result = calc_pipe_0.Calc(project_code, init_num_scenario, substance, equipment,
                                              dangerous_object).result()
                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

                if substance.sub_type.value == 1:  # ЛВЖ+токси
                    result = calc_pipe_1.Calc(project_code, init_num_scenario, substance, equipment,
                                              dangerous_object).result()
                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

            elif equipment.equipment_type.value == 'Tank':
                if substance.sub_type.value == 0:  # ЛВЖ
                    result = calc_tank_0.Calc(project_code, init_num_scenario, substance, equipment,
                                              dangerous_object).result()
                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

                # elif substance.sub_type.value == 1:  # ЛВЖ+токси
                #     result = calc_tank_1.Calc(project_code, init_num_scenario, substance, equipment,
                #                               dangerous_object).result()
                #     for item in result[0]:
                #         # Сохраняем в БД
                #         self._save_calculation(item)
                #     init_num_scenario = result[1]

            elif equipment.equipment_type.value == 'Truck_tank':
                if substance.sub_type.value == 0:  # ЛВЖ
                    result = calc_truc_tank_0.Calc(project_code, init_num_scenario, substance, equipment,
                                                   dangerous_object).result()
                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

            elif equipment.equipment_type.value == 'Technological_device':
                if substance.sub_type.value == 0:  # ЛВЖ
                    result = calc_device_0.Calc(project_code, init_num_scenario, substance, equipment,
                                                dangerous_object).result()

                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

                if substance.sub_type.value == 1:  # ЛВЖ+токси
                    result = calc_device_1.Calc(project_code, init_num_scenario, substance, equipment,
                                                dangerous_object).result()

                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

            elif equipment.equipment_type.value == 'Pump':
                if substance.sub_type.value == 0:  # ЛВЖ
                    result = calc_pump_0.Calc(project_code, init_num_scenario, substance, equipment,
                                              dangerous_object).result()

                    for item in result[0]:
                        # Сохраняем в БД
                        self._save_calculation(item)
                    init_num_scenario = result[1]

    def clear_project_calculations(self) -> None:
        """Очистка всех расчетов"""
        try:
            # Очищаем данные в БД
            with self.db.get_cursor() as cursor:
                cursor.execute("DELETE FROM calculation_results")

            # Если есть доступ к главному окну через которое запущен расчет
            main_window = self.get_main_window()  # нужно реализовать этот метод
            if main_window:
                # Очищаем таблицу результатов
                main_window.calculation_results_widget.table.clearContents()
                main_window.calculation_results_widget.table.setRowCount(0)

                # Очищаем графики рисков если они есть
                if hasattr(main_window.calculation_results_widget, 'statistics_widget'):
                    main_window.calculation_results_widget.statistics_widget.update_statistics([])

                # Обновляем виджет анализа рисков если он есть
                if hasattr(main_window, 'risk_analysis_widget'):
                    main_window.risk_analysis_widget.load_data()

        except Exception as e:
            raise ValueError(f"Не удалось очистить расчеты: {str(e)}")

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
                casualty_risk, injury_risk, expected_damage,
                probability, mass_risk, mass_in_accident,
                mass_in_factor, mass_in_equipment                          
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
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
            calculation.expected_damage,
            calculation.probability,
            calculation.mass_risk,
            calculation.mass_in_accident,
            calculation.mass_in_factor,
            calculation.mass_in_equipment
        )

        self.db.execute_query(query, params)
