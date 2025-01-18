# widgets/calculation_results_widget.py
from typing import List

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QLineEdit,
                             QComboBox, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QCollator
from database.db_connection import DatabaseConnection
from database.repositories.calculation_repo import CalculationResultRepository
from database.repositories.project_repo import ProjectRepository
from models.calculation_result import CalculationResult
from models.equipment import EquipmentType
from models.substance import SubstanceType


class ScenarioNumberItem(QTableWidgetItem):
    """Специальный класс для сортировки номеров сценариев"""
    def __init__(self, text):
        super().__init__(text)
        # Извлекаем числовое значение из строки (убираем 'C' и преобразуем в число)
        self.number = int(text.replace('C', ''))

    def __lt__(self, other):
        """Переопределяем метод сравнения для правильной сортировки"""
        return self.number < other.number

class CalculationResultsWidget(QWidget):
    """Виджет для отображения результатов расчетов"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = CalculationResultRepository(db)
        self.project_repo = ProjectRepository(db)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем основной layout
        layout = QVBoxLayout(self)

        # Создаем панель фильтров
        filter_layout = QHBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по коду проекта...")
        self.search_input.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_input)

        # Фильтр по проекту
        filter_layout.addWidget(QLabel("Проект:"))
        self.project_filter = QComboBox()
        self.project_filter.addItem("Все")
        self.load_projects()
        self.project_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.project_filter)

        # Фильтр по типу оборудования
        filter_layout.addWidget(QLabel("Тип оборудования:"))
        self.equipment_type_filter = QComboBox()
        self.equipment_type_filter.addItem("Все")
        for eq_type in EquipmentType:
            self.equipment_type_filter.addItem(
                EquipmentType.get_display_name(eq_type),
                userData=eq_type
            )
        self.equipment_type_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.equipment_type_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(16)
        self.table.setHorizontalHeaderLabels([
            "ID", "Код проекта", "№ сценария",
            "Оборудование", "Тип оборудования",
            "Тип вещества", "Погибшие", "Пострадавшие",
            "Суммарный ущерб", "dP=2кПа",
            "q=1.4", "Кол.риск(погиб.)", "Частота,1/год",
            "Мав,т", "Моб,т", "Мпф, т"
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(13, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(14, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(15, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Создаем панель с кнопками
        btn_layout = QHBoxLayout()

        self.view_btn = QPushButton("Просмотр")
        self.view_btn.clicked.connect(self.on_view)
        btn_layout.addWidget(self.view_btn)

        btn_layout.addStretch()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

    def load_projects(self):
        """Загрузка списка проектов в фильтр"""
        projects = self.project_repo.get_all()
        for project in projects:
            if project.project_code:  # Только проекты с кодом
                display_text = f"{project.project_code} | {project.name}"
                self.project_filter.addItem(display_text, userData=project.project_code)

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Получаем выбранные фильтры
        project_code = self.project_filter.currentData()
        equipment_type = self.equipment_type_filter.currentData()
        search_text = self.search_input.text().strip()

        # Получаем результаты расчетов
        if project_code:
            results = self.repo.get_by_project(project_code)
        else:
            results = self.repo.get_all()

        # Применяем фильтры
        filtered_results = []
        for result in results:
            # Применяем фильтр по типу оборудования
            if equipment_type and result.equipment_type != equipment_type:
                continue

            # Применяем текстовый поиск
            if search_text and search_text.lower() not in result.project_code.lower():
                continue

            filtered_results.append(result)

        # Находим максимальные значения
        max_total_damage = max((r.total_damage for r in filtered_results), default=0)
        max_p_2 = max((r.p_2 for r in filtered_results), default=0)
        max_q_1_4 = max((r.q_1_4 for r in filtered_results), default=0)
        max_casualties = max((r.casualties for r in filtered_results), default=0)

        # Заполняем таблицу
        self.table.setRowCount(len(filtered_results))

        for i, result in enumerate(filtered_results):
            # ID
            item = QTableWidgetItem(str(result.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Код проекта
            item = QTableWidgetItem(result.project_code)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Номер сценария - используем специальный класс
            scenario_number = f"C{result.scenario_number}"
            item = ScenarioNumberItem(scenario_number)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Оборудование
            item = QTableWidgetItem(result.equipment_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Тип оборудования
            item = QTableWidgetItem(EquipmentType.get_display_name(result.equipment_type))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Тип вещества
            item = QTableWidgetItem(SubstanceType.get_display_name(result.substance_type))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Погибшие
            item = QTableWidgetItem(str(result.casualties))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if result.casualties == max_casualties and max_casualties > 0:
                item.setBackground(QColor(255, 200, 200))  # Красный
            self.table.setItem(i, 6, item)

            # Пострадавшие
            item = QTableWidgetItem(str(result.injured))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

            # Суммарный ущерб
            item = QTableWidgetItem(f"{result.total_damage:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if result.total_damage == max_total_damage and max_total_damage > 0:
                item.setBackground(QColor(255, 255, 200))  # Желтый
            self.table.setItem(i, 8, item)

            # dP=2
            item = QTableWidgetItem(f"{result.p_2:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if result.p_2 == max_p_2 and max_p_2 > 0:
                item.setBackground(QColor(200, 255, 200))  # Зеленый
            self.table.setItem(i, 9, item)

            # q=1.4
            item = QTableWidgetItem(f"{result.q_1_4:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if result.q_1_4 == max_q_1_4 and max_q_1_4 > 0:
                item.setBackground(QColor(200, 200, 255))  # Синий
            self.table.setItem(i, 10, item)

            # Коллективный риск погибшие
            item = QTableWidgetItem(f"{result.casualty_risk:.2e}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 11, item)
            # Коллективный риск погибшие
            item = QTableWidgetItem(f"{result.probability:.2e}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 12, item)

            # Мав,т
            item = QTableWidgetItem(f"{result.mass_in_accident:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 13, item)

            # Моб,т
            item = QTableWidgetItem(f"{result.mass_in_equipment:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 14, item)

            # Мпф,т
            item = QTableWidgetItem(f"{result.mass_in_factor:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 15, item)

        # # Включаем сортировку и сортируем по номеру сценария по умолчанию
        # self.table.setSortingEnabled(True)
        # self.table.sortItems(2)  # 2 - индекс колонки с номером сценария

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_result_id(self) -> int:
        """Получение ID выбранного результата"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_view(self):
        """Обработчик просмотра результата"""
        result_id = self.get_selected_result_id()
        if not result_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите результат для просмотра")
            return

        result = self.repo.get_by_id(result_id)
        if not result:
            QMessageBox.warning(self, "Предупреждение",
                              "Результат не найден")
            return

        # Показываем диалог просмотра
        from .calculation_result_dialog import CalculationResultDialog
        dialog = CalculationResultDialog(result, self)
        dialog.exec()

    def get_all_results(self) -> List[CalculationResult]:
        """Получение всех результатов расчетов из таблицы"""
        results = []

        for row in range(self.table.rowCount()):
            result_id = int(self.table.item(row, 0).text())
            result = self.repo.get_by_id(result_id)
            if result:
                results.append(result)

        return results