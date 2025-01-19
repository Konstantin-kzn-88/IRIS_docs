# template_report_generator.py
from docxtpl import DocxTemplate
from PySide6.QtWidgets import QFileDialog, QMessageBox
import os
import sys
import subprocess

from database.db_connection import DatabaseConnection
from database.repositories.calculation_repo import CalculationResultRepository
from models.dangerous_object import HazardClass


class TemplateReportGenerator:
    """Класс для генерации отчетов на основе шаблона docx"""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.calc_repo = CalculationResultRepository(db)

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

        # Формируем общий контекст
        context = {
            **org_data,
            **opo_data,
            **project_data,
            **equipment_data,
        }

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