# template_report_generator.py
import numpy as np
from docxtpl import DocxTemplate
from PySide6.QtWidgets import QFileDialog, QMessageBox
import os
import sys
import subprocess

import matplotlib.pyplot as plt
import io
from docxtpl import InlineImage

from database.db_connection import DatabaseConnection
from database.repositories.calculation_repo import CalculationResultRepository
from models.dangerous_object import HazardClass
from models.equipment import EquipmentType
from models.substance import SubstanceType


class TemplateReportGenerator:
    """Класс для генерации отчетов на основе шаблона docx"""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.calc_repo = CalculationResultRepository(db)
        self.doc = None  # Добавляем атрибут doc

    def generate_report(self, project_code: str = None, parent=None):
        """
        Генерация отчета на основе шаблона
        Args:
            project_code: Код проекта
            parent: Родительское окно для диалогов
        """
        if not project_code:
            QMessageBox.warning(
                parent,
                "Предупреждение",
                "Не выбран проект для формирования отчета"
            )
            return

        # Открываем диалог выбора шаблона
        template_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Выберите шаблон отчета",
            "",
            "Шаблон Word (*.docx)"
        )

        if not template_path:
            return

        # Открываем диалог сохранения готового отчета
        output_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Сохранить отчет",
            "",
            "Документ Word (*.docx)"
        )

        if not output_path:
            return

        try:
            # Создаем объект шаблона
            doc = DocxTemplate(template_path)
            self.doc = doc  # Сохраняем ссылку на текущий документ для отрисовки диаграммы

            # Получаем все необходимые данные
            context = self._prepare_context(project_code)

            # Заполняем шаблон
            doc.render(context)

            # Сохраняем результат
            doc.save(output_path)

            QMessageBox.information(
                parent,
                "Успешно",
                f"Отчет сохранен в файл:\n{output_path}"
            )

            # Открываем файл
            if sys.platform == 'win32':
                os.startfile(output_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', output_path])
            else:  # linux
                subprocess.call(['xdg-open', output_path])

        except Exception as e:
            QMessageBox.critical(
                parent,
                "Ошибка",
                f"Не удалось сформировать отчет:\n{str(e)}"
            )

    def _prepare_context(self, project_code: str) -> dict:
        """
        Подготовка контекста с данными для шаблона
        Args:
            project_code: Код проекта
        Returns:
            dict: Словарь с данными для шаблона
        """
        # Получаем данные организации
        org_data = self._get_organization_data(project_code)

        # Получаем данные ОПО
        opo_data = self._get_opo_data(project_code)

        # Получаем данные проекта
        project_data = self._get_project_data(project_code)

        # Добавляем данные об оборудовании
        equipment_data = self._get_equipment_data(project_code)

        # Добавляем данные о распределении веществ
        mass_data = self._get_calculation_results(project_code)

        # Добавляем данные о расчетах ПФ
        calc_data = self._get_substance_distribution_data(project_code)

        # Добавляем данные анализа риска
        risk_analysis_data = self._get_risk_analysis_data(project_code)

        # Формируем общий контекст
        context = {
            **org_data,
            **opo_data,
            **project_data,
            **equipment_data,
            **mass_data,
            **calc_data,
            **risk_analysis_data
        }

        # Добавляем диаграммы F/N и F/G
        diagrams_data = self._add_fn_fg_diagrams_to_context(project_code)
        context.update(diagrams_data)

        return context

    def _get_organization_data(self, project_code: str) -> dict:
        """Получение данных организации"""
        query = """
           SELECT org.* FROM organizations org
           JOIN dangerous_objects do ON do.organization_id = org.id
           JOIN projects p ON p.opo_id = do.id
           WHERE p.project_code = ?
       """
        org_data = self.db.execute_query(query, (project_code,))

        if not org_data:
            raise ValueError("Не найдены данные организации")

        org = org_data[0]
        return {
            'org_name': org['name'],
            'org_full_name': org['full_name'],
            'org_form': org['org_form'],
            'head_position': org['head_position'] or '-',
            'head_name': org['head_name'] or '-',
            'legal_address': org['legal_address'] or '-',
            'phone': org['phone'] or '-',
            'fax': org['fax'] or '-',
            'email': org['email'] or '-',
            'license_number': org['license_number'] or '-',
            'license_date': org['license_date'] or '-',
            'ind_safety_system': org['ind_safety_system'] or '-',
            'prod_control': org['prod_control'] or '-',
            'accident_investigation': org['accident_investigation'] or '-',
            'rescue_contract': org['rescue_contract'] or '-',
            'rescue_certificate': org['rescue_certificate'] or '-',
            'fire_contract': org['fire_contract'] or '-',
            'emergency_certificate': org['emergency_certificate'] or '-',
            'material_reserves': org['material_reserves'] or '-',
            'financial_reserves': org['financial_reserves'] or '-'
        }

    def _get_opo_data(self, project_code: str) -> dict:
        """Получение данных ОПО"""
        query = """
           SELECT do.* FROM dangerous_objects do
           JOIN projects p ON p.opo_id = do.id
           WHERE p.project_code = ?
       """
        opo_data = self.db.execute_query(query, (project_code,))

        if not opo_data:
            raise ValueError("Не найдены данные ОПО")

        opo = opo_data[0]
        return {
            'opo_name': opo['name'],
            'reg_number': opo['reg_number'],
            'hazard_class': HazardClass.get_display_name(HazardClass(opo['hazard_class'])),
            'location': opo['location'],
            'employee_count': opo['employee_count'],
            'view_space': f"Класс {opo['view_space']}"
        }

    def _get_project_data(self, project_code: str) -> dict:
        """Получение данных проекта"""
        query = "SELECT * FROM projects WHERE project_code = ?"
        project_data = self.db.execute_query(query, (project_code,))

        if not project_data:
            raise ValueError("Не найдены данные проекта")

        project = project_data[0]
        return {
            'project_name': project['name'],
            'project_code': project['project_code'],
            'project_description': project['description'] or '-',
            'automation_description': project['automation_description'] or '-',
            'dpb_code': project['dpb_code'] or '-',
            'rpz_code': project['rpz_code'] or '-',
            'ifl_code': project['ifl_code'] or '-',
            'gochs_code': project['gochs_code'] or '-',
            'mpb_code': project['mpb_code'] or '-'
        }

    def _get_equipment_data(self, project_code: str) -> dict:
        """Получение данных об оборудовании проекта"""
        query = """
        SELECT 
            be.id,
            be.name,
            be.equipment_type,
            be.component_enterprise,
            be.pressure,
            be.temperature,
            p.diameter_category,
            p.length_meters,
            p.diameter_pipeline,
            p.flow as pipeline_flow,
            pm.pump_type,
            pm.volume as pump_volume,
            pm.flow as pump_flow,
            td.device_type,
            td.volume as device_volume,
            td.degree_filling as device_filling,
            t.tank_type,
            t.volume as tank_volume,
            t.degree_filling as tank_filling,
            tt.pressure_type,
            tt.volume as truck_volume,
            tt.degree_filling as truck_filling,
            c.comp_type,
            c.volume as comp_volume,
            c.flow as comp_flow
        FROM base_equipment be
        LEFT JOIN pipelines p ON p.id = be.id
        LEFT JOIN pumps pm ON pm.id = be.id
        LEFT JOIN technological_devices td ON td.id = be.id
        LEFT JOIN tanks t ON t.id = be.id
        LEFT JOIN truck_tanks tt ON tt.id = be.id
        LEFT JOIN compressors c ON c.id = be.id
        WHERE be.project_id IN (SELECT id FROM projects WHERE project_code = ?)
        ORDER BY be.name
        """

        equipment_data = self.db.execute_query(query, (project_code,))

        if not equipment_data:
            return {'equipment_list': []}

        # Формируем список оборудования
        equipment_list = []

        for eq in equipment_data:
            # Формируем технические характеристики
            tech_specs = []

            # Общие характеристики
            tech_specs.append(f"P={eq['pressure']:.2f} МПа")
            tech_specs.append(f"T={eq['temperature']:.1f} °C")

            # Специфичные характеристики в зависимости от типа
            if eq['equipment_type'] == 'Pipeline':
                tech_specs.append(f"L={eq['length_meters']:.1f} м")
                tech_specs.append(f"D={eq['diameter_pipeline']:.1f} мм")
                if eq['pipeline_flow']:
                    tech_specs.append(f"Q={eq['pipeline_flow']:.2f} кг/с")
                purpose = "Транспортировка опасного вещества"

            elif eq['equipment_type'] == 'Pump':
                if eq['pump_volume']:
                    tech_specs.append(f"V={eq['pump_volume']:.1f} м³")
                if eq['pump_flow']:
                    tech_specs.append(f"Q={eq['pump_flow']:.2f} кг/с")
                purpose = "Перекачивание опасного вещества"

            elif eq['equipment_type'] == 'Technological_device':
                if eq['device_volume']:
                    tech_specs.append(f"V={eq['device_volume']:.1f} м³")
                if eq['device_filling']:
                    tech_specs.append(f"Степень заполнения={eq['device_filling'] * 100:.1f}%")
                purpose = "Проведение технологического процесса"

            elif eq['equipment_type'] in ['Tank', 'Truck_tank']:
                volume_key = 'tank_volume' if eq['equipment_type'] == 'Tank' else 'truck_volume'
                filling_key = 'tank_filling' if eq['equipment_type'] == 'Tank' else 'truck_filling'

                if eq[volume_key]:
                    tech_specs.append(f"V={eq[volume_key]:.1f} м³")
                if eq[filling_key]:
                    tech_specs.append(f"Степень заполнения={eq[filling_key] * 100:.1f}%")
                purpose = "Хранение опасного вещества"

            elif eq['equipment_type'] == 'Compressor':
                if eq['comp_volume']:
                    tech_specs.append(f"V={eq['comp_volume']:.1f} м³")
                if eq['comp_flow']:
                    tech_specs.append(f"Q={eq['comp_flow']:.2f} кг/с")
                purpose = "Компримирование опасного вещества"

            # Добавляем оборудование в список
            equipment_list.append({
                'component': eq['component_enterprise'],
                'name': eq['name'].split('(')[0].strip(),
                'location': "Наземное",
                'quantity': "1",
                'purpose': purpose,
                'specifications': ", ".join(tech_specs)
            })

        return {
            'equipment_list': equipment_list
        }

    def _get_substance_distribution_data(self, project_code: str) -> dict:
        """Получение данных о распределении опасного вещества по оборудованию"""
        query = """
        SELECT 
            be.id,
            be.name,
            be.equipment_type,
            be.component_enterprise,
            be.temperature,
            be.pressure,
            p.diameter_category,
            p.length_meters,
            p.diameter_pipeline,
            p.flow as pipeline_flow,
            pm.pump_type,
            pm.volume as pump_volume,
            pm.flow as pump_flow,
            td.device_type,
            td.volume as device_volume,
            td.degree_filling as device_filling,
            t.tank_type,
            t.volume as tank_volume,
            t.degree_filling as tank_filling,
            tt.pressure_type,
            tt.volume as truck_volume,
            tt.degree_filling as truck_filling,
            c.comp_type,
            c.volume as comp_volume,
            c.flow as comp_flow,
            (SELECT cr.mass_in_equipment 
             FROM calculation_results cr 
             WHERE cr.project_code = ? 
             AND cr.equipment_name = be.name 
             ORDER BY cr.scenario_number DESC 
             LIMIT 1) as mass_in_equipment
        FROM base_equipment be
        LEFT JOIN pipelines p ON p.id = be.id
        LEFT JOIN pumps pm ON pm.id = be.id
        LEFT JOIN technological_devices td ON td.id = be.id
        LEFT JOIN tanks t ON t.id = be.id
        LEFT JOIN truck_tanks tt ON tt.id = be.id
        LEFT JOIN compressors c ON c.id = be.id
        WHERE be.project_id IN (SELECT id FROM projects WHERE project_code = ?)
        ORDER BY be.name
        """

        equipment_data = self.db.execute_query(query, (project_code, project_code))

        if not equipment_data:
            return {'substance_distribution': []}

        components_dict = {}

        for eq in equipment_data:
            component = eq['component_enterprise']
            if not component:
                continue

            if component not in components_dict:
                components_dict[component] = []

            if eq['equipment_type'] == 'Compressor':
                agr_state = "г.ф."
            else:
                agr_state = "ж.ф."

            mass = eq['mass_in_equipment'] if eq['mass_in_equipment'] is not None else 0

            components_dict[component].append({
                'component': component,
                'equipment_name': eq['name'].split('(')[0].strip(),
                'units_count': "1",
                'mass_in_unit': f"{mass:.3f}",
                'mass_in_block': f"{mass:.3f}",
                'state': agr_state,
                'temperature': f"{eq['temperature']:.1f}",
                'pressure': f"{eq['pressure']:.2f}"  # Добавляем давление в МПа
            })

        substance_distribution = []
        total_mass = 0  # Добавляем переменную для подсчета общей массы

        substance_distribution = []
        for component, equipments in components_dict.items():
            for equipment in sorted(equipments, key=lambda x: x['equipment_name']):
                substance_distribution.append(equipment)
                # Добавляем массу к общей сумме
                total_mass += float(equipment['mass_in_unit'])

        return {
            'substance_distribution': substance_distribution,
            'total_substance_mass': f"{total_mass:.3f}"  # Добавляем общую массу в контекст
        }

    def _get_calculation_results(self, project_code: str) -> dict:
        """
        Получение результатов расчета для шаблона отчета
        Args:
            project_code: Код проекта
        Returns:
            dict: Словарь с данными для шаблона
        """
        # Получаем результаты
        results = self.calc_repo.get_by_project(project_code) if project_code else self.calc_repo.get_all()

        if not results:
            return {'calculation_results': []}

        # Формируем список результатов для шаблона
        calculation_results = []

        # Сортируем результаты по номеру сценария
        results = sorted(results, key=lambda x: int(x.scenario_number))

        for i, result in enumerate(results, 1):
            calc_result = {
                'number': i,
                'project_code': result.project_code,
                'scenario_number': result.scenario_number,
                'equipment_name': result.equipment_name,
                'equipment_type': EquipmentType.get_display_name(result.equipment_type),
                'substance_type': SubstanceType.get_display_name(result.substance_type),

                # Тепловое излучение
                'q_10_5': f"{result.q_10_5:.2f}" if result.q_10_5 else "-",
                'q_7_0': f"{result.q_7_0:.2f}" if result.q_7_0 else "-",
                'q_4_2': f"{result.q_4_2:.2f}" if result.q_4_2 else "-",
                'q_1_4': f"{result.q_1_4:.2f}" if result.q_1_4 else "-",

                # Давление
                'p_53': f"{result.p_53:.2f}" if result.p_53 else "-",
                'p_28': f"{result.p_28:.2f}" if result.p_28 else "-",
                'p_12': f"{result.p_12:.2f}" if result.p_12 else "-",
                'p_5': f"{result.p_5:.2f}" if result.p_5 else "-",
                'p_2': f"{result.p_2:.2f}" if result.p_2 else "-",

                # Геометрические параметры
                'l_f': f"{result.l_f:.2f}" if result.l_f else "-",
                'd_f': f"{result.d_f:.2f}" if result.d_f else "-",
                'r_nkpr': f"{result.r_nkpr:.2f}" if result.r_nkpr else "-",
                'r_flash': f"{result.r_flash:.2f}" if result.r_flash else "-",
                'l_pt': f"{result.l_pt:.2f}" if result.l_pt else "-",
                'p_pt': f"{result.p_pt:.2f}" if result.p_pt else "-",

                # Тепловой поток
                'q_600': f"{result.q_600:.2f}" if result.q_600 else "-",
                'q_320': f"{result.q_320:.2f}" if result.q_320 else "-",
                'q_220': f"{result.q_220:.2f}" if result.q_220 else "-",
                'q_120': f"{result.q_120:.2f}" if result.q_120 else "-",

                # Площадь пролива
                's_spill': f"{result.s_spill:.2f}" if result.s_spill else "-",

                # Последствия
                'casualties': str(result.casualties),
                'injured': str(result.injured),

                # Ущерб
                'direct_losses': f"{result.direct_losses:.2f}",
                'liquidation_costs': f"{result.liquidation_costs:.2f}",
                'social_losses': f"{result.social_losses:.2f}",
                'indirect_damage': f"{result.indirect_damage:.2f}",
                'environmental_damage': f"{result.environmental_damage:.2f}",
                'total_damage': f"{result.total_damage:.2f}",

                # Риски и частоты
                'casualty_risk': f"{result.casualty_risk:.2e}",
                'injury_risk': f"{result.injury_risk:.2e}",
                'expected_damage': f"{result.expected_damage:.2e}",
                'probability': f"{result.probability:.2e}",
                'mass_risk': f"{result.mass_risk:.2e}",

                # Массы
                'mass_in_accident': f"{result.mass_in_accident:.2f}",
                'mass_in_factor': f"{result.mass_in_factor:.2f}",
                'mass_in_equipment': f"{result.mass_in_equipment:.2f}"
            }

            calculation_results.append(calc_result)

        return {
            'calculation_results': calculation_results
        }

    def _get_risk_analysis_data(self, project_code: str) -> dict:
        """
        Получение данных анализа риска для шаблона отчета
        Args:
            project_code: Код проекта
        Returns:
            dict: Словарь с данными анализа риска для шаблона
        """
        # Получаем результаты расчетов
        results = self.calc_repo.get_by_project(project_code) if project_code else self.calc_repo.get_all()

        if not results:
            return {
                'risk_statistics': {},
                'critical_scenarios': [],
                'component_analysis': []
            }

        # Формируем статистические показатели
        risk_statistics = {
            'total_scenarios': len(results),
            'max_casualties': max(r.casualties for r in results),
            'max_injured': max(r.injured for r in results),
            'max_damage': f"{max(r.total_damage for r in results):.2f}",
            'total_death_risk': f"{sum(r.casualty_risk for r in results):.2e}",
            'total_injury_risk': f"{sum(r.injury_risk for r in results):.2e}",
            'max_eco_damage': f"{max(r.environmental_damage for r in results):.2f}"
        }

        # Добавляем максимальную частоту аварий с гибелью
        death_scenarios = [r for r in results if r.casualties >= 1]
        max_death_frequency = max((r.probability for r in death_scenarios), default=0)
        risk_statistics['max_death_frequency'] = f"{max_death_frequency:.2e}"

        # Получаем уникальные компоненты
        components = set()
        for result in results:
            component = None
            if hasattr(result, 'component_enterprise') and result.component_enterprise:
                component = result.component_enterprise
            elif hasattr(result, 'equipment_name') and result.equipment_name:
                import re
                match = re.search(r'\((.*?)\)', result.equipment_name)
                if match:
                    component = match.group(1)
            if component:
                components.add(component)

        # Формируем список критических сценариев
        critical_scenarios = []
        for component in sorted(components):
            # Фильтруем результаты для компонента
            component_results = []
            for result in results:
                if (hasattr(result, 'component_enterprise') and
                        result.component_enterprise == component):
                    component_results.append(result)
                elif hasattr(result, 'equipment_name'):
                    match = re.search(r'\((.*?)\)', result.equipment_name)
                    if match and match.group(1) == component:
                        component_results.append(result)

            if not component_results:
                continue

            # Наиболее опасный сценарий
            most_dangerous = max(component_results, key=lambda x: x.total_damage)
            critical_scenarios.append({
                'component': component,
                'scenario_type': "Наиболее опасный",
                'scenario_number': str(most_dangerous.scenario_number),
                'equipment': most_dangerous.equipment_name,
                'casualties': str(most_dangerous.casualties),
                'injured': str(most_dangerous.injured),
                'total_damage': f"{most_dangerous.total_damage:.2f}",
                'probability': f"{most_dangerous.probability:.2e}"
            })

            # Наиболее вероятный сценарий
            most_probable = max(component_results, key=lambda x: x.probability)
            critical_scenarios.append({
                'component': component,
                'scenario_type': "Наиболее вероятный",
                'scenario_number': str(most_probable.scenario_number),
                'equipment': most_probable.equipment_name,
                'casualties': str(most_probable.casualties),
                'injured': str(most_probable.injured),
                'total_damage': f"{most_probable.total_damage:.2f}",
                'probability': f"{most_probable.probability:.2e}"
            })

        # Формируем анализ по компонентам
        from models.risk_analysis import ComponentRiskAnalysis
        from models.dangerous_object import DangerousObject

        dangerous_object = None
        if project_code:
            query = """
                SELECT do.* FROM dangerous_objects do
                JOIN projects p ON p.opo_id = do.id
                WHERE p.project_code = ?
            """
            opo_data = self.db.execute_query(query, (project_code,))
            if opo_data:
                from models.dangerous_object import DangerousObject
                dangerous_object = DangerousObject.from_dict(dict(opo_data[0]))

        component_analysis = []
        for i, component in enumerate(sorted(components), 1):
            analysis = ComponentRiskAnalysis.calculate_for_component(
                component, results, dangerous_object
            )

            if not analysis:
                continue

            component_analysis.append({
                'number': str(i),
                'component': analysis.component_name,
                'max_damage': f"{analysis.max_damage:.2f}",
                'max_eco_damage': f"{analysis.max_eco_damage:.2f}",
                'max_casualties': str(analysis.max_casualties),
                'max_injured': str(analysis.max_injured),
                'collective_death_risk': f"{analysis.collective_death_risk:.2e}",
                'collective_injury_risk': f"{analysis.collective_injury_risk:.2e}",
                # все поля берем из analysis
                'individual_death_risk': f"{analysis.individual_death_risk:.2e}",
                'individual_injury_risk': f"{analysis.individual_injury_risk:.2e}",
                'risk_level_ppm': f"{analysis.risk_level_ppm:.2f}",
                'risk_level_dbr': f"{analysis.risk_level_dbr:.2f}",
                'max_death_frequency': f"{analysis.max_death_frequency:.2e}"
            })

        # Возвращаем все данные анализа риска
        return {
            'risk_statistics': risk_statistics,
            'critical_scenarios': critical_scenarios,
            'component_analysis': component_analysis
        }


    def _add_fn_fg_diagrams_to_context(self, project_code: str) -> dict:
        """
        Создание F/N и F/G диаграмм и подготовка их для вставки в шаблон
        Args:
            project_code: Код проекта
        Returns:
            dict: Словарь с изображением диаграмм для шаблона
        """
        results = self.calc_repo.get_by_project(project_code) if project_code else self.calc_repo.get_all()

        if not results:
            return {'fn_fg_diagrams': None}

        # Создаем диаграммы
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

        # F/N диаграмма
        casualty_data = [(r.probability, r.casualties) for r in results if r.casualties > 0]
        sum_data = self._sum_data_for_fn(casualty_data)

        if casualty_data:
            people, probability = list(sum_data.keys()), list(sum_data.values())
            # для сплошных линий
            chart_line_x = []
            chart_line_y = []
            for i in people:
                if people[0] == i:
                    chart_line_x.extend([0, i, i, i])
                    chart_line_y.extend([probability[people.index(i)], probability[people.index(i)], None, None])
                elif people[-1] == i:
                    chart_line_x.extend([people[people.index(i)-1], people[people.index(i)-1], i, i])
                    chart_line_y.extend([probability[people.index(i)], probability[people.index(i)], probability[people.index(i)], probability[people.index(i)]])
                    break
                else:
                    chart_line_x.extend([people[people.index(i) - 1], i, i, i])
                    chart_line_y.extend([probability[people.index(i)], probability[people.index(i)], None, None])

            # для пунктирных линий
            chart_dot_line_x = []
            chart_dot_line_y = []
            for i in people:
                if i == people[-1]:
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[people.index(i)], probability[people.index(i)]])
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[people.index(i)], 0])
                    break
                chart_dot_line_x.extend([i, i])
                chart_dot_line_y.extend([probability[people.index(i)], probability[people.index(i) + 1]])


            ax1.semilogy(chart_line_x, chart_line_y, color='b', linestyle='-', marker='.')
            # После отрисовки сплошных линий добавляем отрисовку пунктирных
            ax1.semilogy(chart_dot_line_x, chart_dot_line_y, color='b', linestyle='--', marker='.')
            ax1.grid(True)
            ax1.set_xlabel('N, число погибших')
            ax1.set_ylabel('F, частота событий с N и более погибшими, 1/год')
            ax1.set_title('F/N диаграмма')

        # F/G диаграмма
        damage_data = [(r.probability, r.total_damage) for r in results if r.total_damage > 0]
        sum_data = self._sum_data_for_fg(damage_data)

        if damage_data:
            damage, probability = list(sum_data.keys()), list(sum_data.values())
            # для сплошных линий
            chart_line_x = []
            chart_line_y = []
            for i in damage:
                if damage[0] == i:
                    chart_line_x.extend([0, i, i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], None, None])
                elif damage[-1] == i:
                    chart_line_x.extend([damage[damage.index(i)-1], damage[damage.index(i)-1], i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], probability[damage.index(i)], probability[damage.index(i)]])
                    break
                else:
                    chart_line_x.extend([damage[damage.index(i) - 1], i, i, i])
                    chart_line_y.extend([probability[damage.index(i)], probability[damage.index(i)], None, None])

            # для пунктирных линий
            chart_dot_line_x = []
            chart_dot_line_y = []
            for i in damage:
                if i == damage[-1]:
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[damage.index(i)], probability[damage.index(i)]])
                    chart_dot_line_x.extend([i, i])
                    chart_dot_line_y.extend([probability[damage.index(i)], 0])
                    break
                chart_dot_line_x.extend([i, i])
                chart_dot_line_y.extend([probability[damage.index(i)], probability[damage.index(i) + 1]])

            ax2.semilogy(chart_line_x, chart_line_y, color='r', linestyle='-', marker='.')
            ax2.semilogy(chart_dot_line_x, chart_dot_line_y, color='r', linestyle='--', marker='.')
            ax2.grid(True)
            ax2.set_xlabel('G, ущерб, млн.руб')
            ax2.set_ylabel('F, частота событий с ущербом G и более, 1/год')
            ax2.set_title('F/G диаграмма')

        plt.tight_layout()

        # Сохраняем во временный буфер
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)

        # Закрываем figure
        plt.close()

        return {'fn_fg_diagrams': InlineImage(self.doc, img_buffer)}


    def _sum_data_for_fn(self, data: list):
        '''
        Функция вычисления суммирования вероятностей F при которой пострадало не менее N человек
        :param data: данные вида [[3.8e-08, 1],[5.8e-08, 2],[1.1e-08, 1]..]
        :return: данные вида: {1: 0.00018, 2: 0.012, 3: 6.9008e-06, 4: 3.8e-08, 5: 7.29e-05}
        '''
        uniq = set(sorted([i[1] for i in data]))
        result = dict(zip(uniq, [0] * len(uniq)))

        for item_data in data:
            for item_uniq in uniq:
                if item_data[1] >= item_uniq:
                    result[item_uniq] = result[item_uniq] + item_data[0]

        if 0 in result:
            del result[0]  # удалить суммарную вероятность где пострадало 0 человек
        return result

    def _sum_data_for_fg(self, data: list):
        '''
        Функция вычисления суммирования вероятностей F при которой ущерб не менее G млн.руб
        :param data: данные вида [[3.8e-08, 1.2],[5.8e-08, 0.2],[1.1e-08, 12.4]..]
        :return: данные вида: {0.2: 0.00018, 1: 0.012, 3: 6.9008e-06, 5: 3.8e-08, 6.25: 7.29e-05}
        '''
        uniq = np.arange(0, max([i[1] for i in data])+max([i[1] for i in data]) / 7, max([i[1] for i in data]) / 7)

        result = dict(zip(uniq, [0] * len(uniq)))

        for item_data in data:
            for item_uniq in uniq:
                if item_data[1] >= item_uniq:
                    result[item_uniq] = result[item_uniq] + item_data[0]

        del result[0]  # удалить суммарную вероятность где ущерб 0
        return result