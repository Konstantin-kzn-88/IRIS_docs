# main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QTreeWidget,
                             QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                             QStackedWidget, QMenuBar, QMenu, QStatusBar,
                             QToolBar, QStyle)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from database.db_connection import DatabaseConnection
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


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.setWindowTitle("Промышленная безопасность")
        self.setMinimumSize(1024, 768)

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

        # Создаем панель инструментов
        self.create_toolbar()

        # Создаем статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

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

    def create_tree_items(self):
        """Создание элементов дерева навигации"""
        # Организации
        self.org_item = QTreeWidgetItem(["Организации"])
        self.tree.addTopLevelItem(self.org_item)

        # Опасные производственные объекты
        self.opo_item = QTreeWidgetItem(["Опасные производственные объекты"])
        self.tree.addTopLevelItem(self.opo_item)

        # Проекты
        self.project_item = QTreeWidgetItem(["Проекты"])
        self.tree.addTopLevelItem(self.project_item)

        # Вещества
        self.substance_item = QTreeWidgetItem(["Вещества"])
        self.tree.addTopLevelItem(self.substance_item)

        # Оборудование
        self.equipment_item = QTreeWidgetItem(["Оборудование"])
        self.equipment_item.addChild(QTreeWidgetItem(["Трубопроводы"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Насосы"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Резервуары"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Технологические устройства"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Автоцистерны"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Компрессоры"]))
        self.tree.addTopLevelItem(self.equipment_item)

        # Расчеты
        self.calc_item = QTreeWidgetItem(["Расчеты и отчеты"])
        self.calc_item.addChild(QTreeWidgetItem(["Результаты расчетов"]))
        self.calc_item.addChild(QTreeWidgetItem(["Анализ рисков"]))
        self.calc_item.addChild(QTreeWidgetItem(["Статистика"]))
        self.tree.addTopLevelItem(self.calc_item)

    def create_menu(self):
        """Создание главного меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = QMenu("&Файл", self)
        file_menu.addAction("Выход", self.close)
        menubar.addMenu(file_menu)

        # Меню Справочники
        ref_menu = QMenu("&Справочники", self)
        ref_menu.addAction("Организации", self.show_organizations)
        ref_menu.addAction("Опасные производственные объекты", self.show_dangerous_objects)
        ref_menu.addAction("Проекты", self.show_projects)
        ref_menu.addAction("Вещества", self.show_substances)
        ref_menu.addSeparator()
        ref_menu.addAction("Трубопроводы", self.show_pipelines)
        ref_menu.addAction("Насосы", self.show_pumps)
        ref_menu.addAction("Резервуары", self.show_tanks)
        ref_menu.addAction("Технологические устройства", self.show_tech_devices)
        ref_menu.addAction("Автоцистерны", self.show_truck_tanks)
        ref_menu.addAction("Компрессоры", self.show_compressors)
        menubar.addMenu(ref_menu)

        # Меню Отчеты
        report_menu = QMenu("&Отчеты", self)
        report_menu.addAction("Статистика по ОПО")
        report_menu.addAction("Анализ рисков")
        menubar.addMenu(report_menu)

        # Меню Помощь
        help_menu = QMenu("&Помощь", self)
        help_menu.addAction("О программе", self.show_about)
        menubar.addMenu(help_menu)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)

        # Добавляем кнопки на панель инструментов
        toolbar.addAction(QAction("Организации", self,
                                triggered=self.show_organizations))
        toolbar.addAction(QAction("ОПО", self,
                                triggered=self.show_dangerous_objects))
        toolbar.addAction(QAction("Проекты", self,
                                triggered=self.show_projects))
        toolbar.addAction(QAction("Вещества", self,
                                triggered=self.show_substances))
        toolbar.addSeparator()
        toolbar.addAction(QAction("Трубопроводы", self,
                                triggered=self.show_pipelines))
        toolbar.addAction(QAction("Насосы", self,
                                triggered=self.show_pumps))
        toolbar.addAction(QAction("Резервуары", self,
                                triggered=self.show_tanks))
        toolbar.addAction(QAction("Технологические устройства", self,
                                triggered=self.show_tech_devices))
        toolbar.addAction(QAction("Автоцистерны", self,
                                triggered=self.show_truck_tanks))
        toolbar.addAction(QAction("Компрессоры", self,
                                  triggered=self.show_compressors))

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
                         "Программа учета опасных производственных объектов\n"
                         "Версия 1.0\n\n"
                         "© 2024 Все права защищены")