# main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QTreeWidget,
                             QTreeWidgetItem, QHBoxLayout, QVBoxLayout,
                             QStackedWidget, QMenuBar, QMenu, QStatusBar)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from widgets.organizations_widget import OrganizationsWidget
from widgets.dangerous_objects_widget import DangerousObjectsWidget
from widgets.projects_widget import ProjectsWidget
from widgets.substances_widget import SubstancesWidget  # Добавляем импорт


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

        # Placeholder для остальных разделов
        for _ in range(3):  # Уменьшаем количество заглушек, так как добавили виджет веществ
            placeholder = QWidget()
            placeholder.setLayout(QVBoxLayout())
            self.content.addWidget(placeholder)

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
        self.equipment_item.addChild(QTreeWidgetItem(["Технологические устройства"]))
        self.equipment_item.addChild(QTreeWidgetItem(["Резервуары"]))
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
        ref_menu.addAction("Вещества", self.show_substances)  # Добавляем пункт меню
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
        elif item_text == "Вещества":  # Добавляем обработку вкладки веществ
            self.content.setCurrentWidget(self.substances_widget)
        # TODO: Добавить обработку остальных разделов

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

    def show_substances(self):  # Добавляем метод для показа веществ
        """Показать раздел веществ"""
        self.tree.setCurrentItem(self.substance_item)
        self.content.setCurrentWidget(self.substances_widget)

    def show_about(self):
        """Показать информацию о программе"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, "О программе",
                         "Программа учета опасных производственных объектов\n"
                         "Версия 1.0\n\n"
                         "© 2024 Все права защищены")