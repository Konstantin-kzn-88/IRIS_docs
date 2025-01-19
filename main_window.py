# main_window.py
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QWidget, QTreeWidget,
                               QTreeWidgetItem, QHBoxLayout, QStackedWidget, QMenu, QStatusBar,
                               QToolBar, QFileDialog, QMessageBox)
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon

from calculation_manager import CalculationManager
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from widgets.calculation_results_widget import CalculationResultsWidget
from widgets.organizations_widget import OrganizationsWidget
from widgets.dangerous_objects_widget import DangerousObjectsWidget
from widgets.projects_widget import ProjectsWidget
from widgets.substances_widget import SubstancesWidget
from widgets.pipelines_widget import PipelinesWidget
from widgets.pumps_widget import PumpsWidget
from widgets.tanks_widget import TanksWidget
from widgets.technological_devices_widget import TechnologicalDevicesWidget
from widgets.truck_tanks_widget import TruckTanksWidget
from widgets.compressors_widget import CompressorsWidget
from widgets.risk_analysis_widget import RiskAnalysisWidget

from report.template_report_generator import TemplateReportGenerator

from report.report_generator import ReportGenerator

import os
import sys
import subprocess




class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        # Инициализируем менеджер расчетов с ссылкой на главное окно
        self.calculation_manager = CalculationManager(db, self)

        self.setWindowTitle("IRIS_docs")
        self.setMinimumSize(1024, 768)

        self.__set_ico()
        self.path_ico = str(Path(os.getcwd()))

        # Добавляем репозиторий проектов
        self.project_repo = ProjectRepository(db)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Создаем горизонтальный layout
        layout = QHBoxLayout(central_widget)

        # Создаем дерево навигации
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Навигация")
        self.tree.setMinimumWidth(250)
        self.tree.currentItemChanged.connect(self.on_tree_item_changed)

        # Добавляем разделы в дерево
        self.create_tree_items()

        # Создаем стек виджетов для контента
        self.content = QStackedWidget()

        # Инициализируем виджеты
        self.init_widgets()

        # Добавляем виджеты в layout
        layout.addWidget(self.tree)
        layout.addWidget(self.content, stretch=1)

        # Создаем меню
        self.create_menu()

        # Создаем статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Виджет результатов расчетов
        self.calculation_results_widget = CalculationResultsWidget(self.db)
        self.content.addWidget(self.calculation_results_widget)

    def __set_ico(self):
        main_ico = QIcon('main_ico.ico')
        self.setWindowIcon(main_ico)

    def init_widgets(self):
        """Инициализация виджетов"""
        # Виджет организаций
        self.organizations_widget = OrganizationsWidget(self.db)
        self.content.addWidget(self.organizations_widget)

        # Виджет ОПО
        self.dangerous_objects_widget = DangerousObjectsWidget(self.db)
        self.content.addWidget(self.dangerous_objects_widget)

        # Виджет проектов
        self.projects_widget = ProjectsWidget(self.db)
        self.content.addWidget(self.projects_widget)

        # Виджет веществ
        self.substances_widget = SubstancesWidget(self.db)
        self.content.addWidget(self.substances_widget)

        # Виджет трубопроводов
        self.pipelines_widget = PipelinesWidget(self.db)
        self.content.addWidget(self.pipelines_widget)

        # Виджет насосов
        self.pumps_widget = PumpsWidget(self.db)
        self.content.addWidget(self.pumps_widget)

        # Виджет резервуаров
        self.tanks_widget = TanksWidget(self.db)
        self.content.addWidget(self.tanks_widget)

        # Виджет технологических устройств
        self.tech_devices_widget = TechnologicalDevicesWidget(self.db)
        self.content.addWidget(self.tech_devices_widget)

        # Виджет автоцистерн
        self.truck_tanks_widget = TruckTanksWidget(self.db)
        self.content.addWidget(self.truck_tanks_widget)

        # Виджет компрессоров
        self.compressors_widget = CompressorsWidget(self.db)
        self.content.addWidget(self.compressors_widget)

        # Добавляем виджет анализа риска
        self.risk_analysis_widget = RiskAnalysisWidget(self.db)
        self.content.addWidget(self.risk_analysis_widget)

    def generate_word_report(self):
        """Генерация отчета в Word"""
        try:
            # Получаем активный проект из текущей вкладки расчетов
            project_code = None
            if self.calculation_results_widget:
                # Берем код проекта из первой строки таблицы результатов
                if self.calculation_results_widget.table.rowCount() > 0:
                    project_code = self.calculation_results_widget.table.item(0, 1).text()

            # Открываем диалог сохранения
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                "",
                "Документ Word (*.docx)"
            )

            if file_path:
                # Создаем генератор отчетов
                report_gen = ReportGenerator(self.db)

                # Генерируем отчет
                report_gen.generate_full_report(file_path, project_code)

                QMessageBox.information(
                    self,
                    "Успешно",
                    f"Отчет сохранен в файл:\n{file_path}"
                )

                # Открываем файл
                if sys.platform == 'win32':
                    os.startfile(file_path)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', file_path])
                else:  # linux
                    subprocess.call(['xdg-open', file_path])

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сформировать отчет:\n{str(e)}"
            )

    def generate_report_from_template(self):
        """Генерация отчета на основе шаблона"""
        try:
            # Получаем код проекта
            project_code = None
            if self.calculation_results_widget:
                if self.calculation_results_widget.table.rowCount() > 0:
                    project_code = self.calculation_results_widget.table.item(0, 1).text()

            report_gen = TemplateReportGenerator(self.db)
            report_gen.generate_report(project_code)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сформировать отчет:\n{str(e)}"
            )

    def create_tree_items(self):
        """Создание элементов дерева навигации"""
        # Организации
        self.org_item = QTreeWidgetItem(["Организации"])
        self.org_item.setIcon(0, QIcon("ico/organization.png"))
        self.tree.addTopLevelItem(self.org_item)

        # Опасные производственные объекты
        self.opo_item = QTreeWidgetItem(["Опасные производственные объекты"])
        self.opo_item.setIcon(0, QIcon("ico/factory.png"))
        self.tree.addTopLevelItem(self.opo_item)

        # Проекты
        self.project_item = QTreeWidgetItem(["Проекты"])
        self.project_item.setIcon(0, QIcon("ico/book.png"))
        self.tree.addTopLevelItem(self.project_item)

        # Вещества
        self.substance_item = QTreeWidgetItem(["Вещества"])
        self.substance_item.setIcon(0, QIcon("ico/subs.png"))
        self.tree.addTopLevelItem(self.substance_item)

        # Оборудование
        self.equipment_item = QTreeWidgetItem(["Оборудование"])
        self.equipment_item.setIcon(0, QIcon("ico/data_base.png"))

        # Создаем дочерние элементы с иконками
        pipeline_item = QTreeWidgetItem(["Трубопроводы"])
        pipeline_item.setIcon(0, QIcon("ico/pipeline.png"))
        self.equipment_item.addChild(pipeline_item)

        pump_item = QTreeWidgetItem(["Насосы"])
        pump_item.setIcon(0, QIcon("ico/pump.png"))
        self.equipment_item.addChild(pump_item)

        tank_item = QTreeWidgetItem(["Резервуары"])
        tank_item.setIcon(0, QIcon("ico/tank.png"))
        self.equipment_item.addChild(tank_item)

        tech_item = QTreeWidgetItem(["Технологические устройства"])
        tech_item.setIcon(0, QIcon("ico/tech_device.png"))
        self.equipment_item.addChild(tech_item)

        truck_item = QTreeWidgetItem(["Автоцистерны"])
        truck_item.setIcon(0, QIcon("ico/truck.png"))
        self.equipment_item.addChild(truck_item)

        compressor_item = QTreeWidgetItem(["Компрессоры"])
        compressor_item.setIcon(0, QIcon("ico/compressor.png"))
        self.equipment_item.addChild(compressor_item)

        self.tree.addTopLevelItem(self.equipment_item)

        # Расчеты
        self.calc_item = QTreeWidgetItem(["Расчеты и отчеты"])
        self.calc_item.setIcon(0, QIcon("ico/calculator.png"))
        result_item = QTreeWidgetItem(["Результаты расчетов"])
        result_item.setIcon(0, QIcon("ico/results.png"))
        self.calc_item.addChild(result_item)
        risk_item = QTreeWidgetItem(["Анализ риска"])
        risk_item.setIcon(0, QIcon("ico/risk.png"))
        self.calc_item.addChild(risk_item)
        self.tree.addTopLevelItem(self.calc_item)


    def show_calculation_results(self):
        """Показать раздел результатов расчетов"""
        calc_item = self.calc_item.child(0)  # Первый дочерний элемент
        self.tree.setCurrentItem(calc_item)
        self.content.setCurrentWidget(self.calculation_results_widget)

    def create_menu(self):
        """Создание главного меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = QMenu("&Файл", self)

        # Создаем действия с иконками
        calculate_action = QAction(QIcon("ico/calculator.png"), "Расчет", self)
        calculate_action.triggered.connect(self.show_calculation_dialog)

        report_action = QAction(QIcon("ico/save.png"), "Вывод результатов расчета", self)
        report_action.triggered.connect(self.generate_word_report)

        # В методе create_menu() добавить:
        template_report_action = QAction(QIcon("ico/template.png"), "Отчет по шаблону", self)
        template_report_action.triggered.connect(self.generate_report_from_template)

        exit_action = QAction(QIcon("ico/exit.png"), "Выход", self)
        exit_action.triggered.connect(self.close)


        # Добавляем действия в меню
        file_menu.addAction(calculate_action)
        file_menu.addAction(report_action)
        file_menu.addAction(template_report_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        menubar.addMenu(file_menu)

        # Меню Помощь
        help_menu = QMenu("&Помощь", self)
        help_menu.addAction("О программе", self.show_about)
        menubar.addMenu(help_menu)



    def show_calculation_dialog(self):
        """Показать диалог расчета"""
        from calculation_dialog import CalculationDialog
        dialog = CalculationDialog(self.db, self)
        dialog.exec()

    def on_tree_item_changed(self, current, previous):
        """Обработчик смены элемента в дереве навигации"""
        if not current:
            return

        item_text = current.text(0)

        # Определяем индекс в стеке виджетов
        if item_text == "Организации":
            self.content.setCurrentWidget(self.organizations_widget)
        elif item_text == "Опасные производственные объекты":
            self.content.setCurrentWidget(self.dangerous_objects_widget)
        elif item_text == "Проекты":
            self.content.setCurrentWidget(self.projects_widget)
        elif item_text == "Вещества":
            self.content.setCurrentWidget(self.substances_widget)
        elif item_text == "Трубопроводы":
            self.content.setCurrentWidget(self.pipelines_widget)
        elif item_text == "Насосы":
            self.content.setCurrentWidget(self.pumps_widget)
        elif item_text == "Резервуары":
            self.content.setCurrentWidget(self.tanks_widget)
        elif item_text == "Технологические устройства":
            self.content.setCurrentWidget(self.tech_devices_widget)
        elif item_text == "Автоцистерны":
            self.content.setCurrentWidget(self.truck_tanks_widget)
        elif item_text == "Компрессоры":
            self.content.setCurrentWidget(self.compressors_widget)
        # В методе on_tree_item_changed добавить:
        elif item_text == "Результаты расчетов":
            self.content.setCurrentWidget(self.calculation_results_widget)
        elif item_text == "Анализ риска":
            self.content.setCurrentWidget(self.risk_analysis_widget)

            # Получаем данные из таблицы результатов
            results_table = self.calculation_results_widget.table
            project_code = None
            opo_id = None

            # print("Rows in results table:", results_table.rowCount())  # Отладочный вывод

            if results_table and results_table.rowCount() > 0:
                # Перебираем первые несколько строк для гарантии
                for row in range(min(5, results_table.rowCount())):
                    project_code_item = results_table.item(row, 1)  # Столбец с кодом проекта
                    if project_code_item:
                        project_code = project_code_item.text().strip()
                        # print(f"Found project code in row {row}: {project_code}")  # Отладочный вывод
                        if project_code:
                            break

                if project_code:
                    # Находим проект по коду
                    project = next((p for p in self.project_repo.get_all()
                                    if p.project_code == project_code), None)

                    # print(f"Project found: {project is not None}")  # Отладочный вывод

                    # Если нашли проект, получаем его ОПО
                    if project:
                        opo_id = project.opo_id
                        # print(f"OPO ID: {opo_id}")  # Отладочный вывод

            # Получаем все результаты расчетов для проекта
            calculation_results = self.calculation_results_widget.get_all_results()

            # Загружаем данные в виджет анализа риска и обновляем статистику и графики
            self.risk_analysis_widget.load_data(project_code=project_code, opo_id=opo_id)
            self.risk_analysis_widget.statistics_widget.update_statistics(calculation_results)

        self.statusBar.showMessage(f"Выбран раздел: {item_text}")

    def show_organizations(self):
        """Показать раздел организаций"""
        self.tree.setCurrentItem(self.org_item)
        self.content.setCurrentWidget(self.organizations_widget)

    def show_dangerous_objects(self):
        """Показать раздел ОПО"""
        self.tree.setCurrentItem(self.opo_item)
        self.content.setCurrentWidget(self.dangerous_objects_widget)

    def show_projects(self):
        """Показать раздел проектов"""
        self.tree.setCurrentItem(self.project_item)
        self.content.setCurrentWidget(self.projects_widget)

    def show_substances(self):
        """Показать раздел веществ"""
        self.tree.setCurrentItem(self.substance_item)
        self.content.setCurrentWidget(self.substances_widget)

    def show_pipelines(self):
        """Показать раздел трубопроводов"""
        pipeline_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Трубопроводы":
                pipeline_item = child
                break
        if pipeline_item:
            self.tree.setCurrentItem(pipeline_item)
            self.content.setCurrentWidget(self.pipelines_widget)

    def show_pumps(self):
        """Показать раздел насосов"""
        pump_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Насосы":
                pump_item = child
                break
        if pump_item:
            self.tree.setCurrentItem(pump_item)
            self.content.setCurrentWidget(self.pumps_widget)

    def show_tanks(self):
        """Показать раздел резервуаров"""
        tank_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Резервуары":
                tank_item = child
                break
        if tank_item:
            self.tree.setCurrentItem(tank_item)
            self.content.setCurrentWidget(self.tanks_widget)

    def show_tech_devices(self):
        """Показать раздел технологических устройств"""
        tech_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Технологические устройства":
                tech_item = child
                break
        if tech_item:
            self.tree.setCurrentItem(tech_item)
            self.content.setCurrentWidget(self.tech_devices_widget)

    def show_truck_tanks(self):
        """Показать раздел автоцистерн"""
        truck_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Автоцистерны":
                truck_item = child
                break
        if truck_item:
            self.tree.setCurrentItem(truck_item)
            self.content.setCurrentWidget(self.truck_tanks_widget)

    def show_compressors(self):
        """Показать раздел компрессоров"""
        compressor_item = None
        for i in range(self.equipment_item.childCount()):
            child = self.equipment_item.child(i)
            if child.text(0) == "Компрессоры":
                compressor_item = child
                break
        if compressor_item:
            self.tree.setCurrentItem(compressor_item)
            self.content.setCurrentWidget(self.compressors_widget)

    def show_about(self):
        """Показать информацию о программе"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, "О программе",
                         "Программа для расчета рисков на опасных производственных объектах\n"
                         '"IRIS" - Industrial Risk Impact Simulator\n\n'
                         "Версия 1.0\n\n"
                         "© 2024 Все права защищены")