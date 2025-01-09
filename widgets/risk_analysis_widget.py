# widgets/risk_analysis_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QLabel, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from database.db_connection import DatabaseConnection
from database.repositories.calculation_repo import CalculationResultRepository
from database.repositories.dangerous_object_repo import DangerousObjectRepository
from models.risk_analysis import ComponentRiskAnalysis
from typing import List, Optional
from .risk_statistics_widget import RiskStatisticsWidget


class RiskAnalysisWidget(QWidget):
    """Виджет для отображения анализа риска"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.calc_repo = CalculationResultRepository(db)
        self.opo_repo = DangerousObjectRepository(db)
        self.statistics_widget = RiskStatisticsWidget()
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Добавляем виджет статистики
        layout.addWidget(self.statistics_widget)

        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "№ п/п",
            "Составляющая",
            "Макс. ущерб, млн.руб",
            "Макс. экологический ущерб, млн.руб",
            "Макс. количество погибших, чел",
            "Макс. количество пострадавших, чел",
            "Коллективный риск гибели, чел/год",
            "Коллективный риск ранения, чел/год",
            "Индивидуальный риск гибели, чел/год",
            "Индивидуальный риск ранения, чел/год",
            "Уровень риска, ppm",
            "Уровень риска, дБR",
            "Частота аварии с гибелью не менее одного человека, 1/год"
        ])

        # Настраиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        # Добавляем таблицу в layout
        layout.addWidget(self.table)

    # иии
    def load_data(self, project_code: str = None, opo_id: Optional[int] = None):
        """Загрузка данных анализа риска"""
        if not project_code:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Не выполнены расчеты. Сначала выполните расчет сценариев для проекта."
            )
            return

        if not self.check_calculation_status(project_code):
            return

        # Очищаем таблицу
        self.table.clearContents()
        self.table.setRowCount(0)

        # Получаем результаты расчетов
        results = self.calc_repo.get_by_project(project_code)
        dangerous_object = self.opo_repo.get_by_id(opo_id) if opo_id else None

        print(f"Got {len(results)} results and dangerous_object: {dangerous_object is not None}")

        # Получаем уникальные компоненты из component_enterprise или equipment_name
        components = set()
        for result in results:
            component = None
            if hasattr(result, 'component_enterprise') and result.component_enterprise:
                # Если есть компонент предприятия, используем его
                component = result.component_enterprise
            elif hasattr(result, 'equipment_name') and result.equipment_name:
                # Извлекаем компонент из текста в скобках
                import re
                match = re.search(r'\((.*?)\)', result.equipment_name)
                if match:
                    component = match.group(1)

            if component:
                components.add(component)

        print(f"Found {len(components)} unique components:", components)

        print(f"Found {len(components)} unique components")

        # Рассчитываем анализ риска для каждого компонента
        analyses = []
        for component in sorted(components):
            analysis = ComponentRiskAnalysis.calculate_for_component(
                component, results, dangerous_object
            )
            if analysis:
                analyses.append(analysis)

        # Заполняем таблицу
        self.table.setRowCount(len(analyses))

        for i, analysis in enumerate(analyses):
            # Номер п/п
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, item)

            # Составляющая
            item = QTableWidgetItem(analysis.component_name)
            self.table.setItem(i, 1, item)

            # Максимальный ущерб
            item = QTableWidgetItem(f"{analysis.max_damage:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 2, item)

            # Максимальный экологический ущерб
            item = QTableWidgetItem(f"{analysis.max_eco_damage:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 3, item)

            # Максимальное количество погибших
            item = QTableWidgetItem(str(analysis.max_casualties))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 4, item)

            # Максимальное количество пострадавших
            item = QTableWidgetItem(str(analysis.max_injured))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 5, item)

            # Коллективный риск гибели
            item = QTableWidgetItem(f"{analysis.collective_death_risk:.2e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 6, item)

            # Коллективный риск ранения
            item = QTableWidgetItem(f"{analysis.collective_injury_risk:.2e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 7, item)

            # Индивидуальный риск гибели
            item = QTableWidgetItem(f"{analysis.individual_death_risk:.2e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 8, item)

            # Индивидуальный риск ранения
            item = QTableWidgetItem(f"{analysis.individual_injury_risk:.2e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 9, item)

            # Уровень риска, ppm
            item = QTableWidgetItem(f"{analysis.risk_level_ppm:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 10, item)

            # Уровень риска, дБR
            if analysis.risk_level_dbr == float('-inf'):
                item = QTableWidgetItem("-∞")
            else:
                item = QTableWidgetItem(f"{analysis.risk_level_dbr:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 11, item)

            # Частота аварии с гибелью
            item = QTableWidgetItem(f"{analysis.max_death_frequency:.2e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 12, item)

        # Форматируем таблицу
        self._format_table()

        # Обновляем статистику
        self.statistics_widget.update_statistics(results)

    def _format_table(self):
        """Форматирование таблицы"""
        # Устанавливаем фиксированную ширину первой колонки
        self.table.setColumnWidth(0, 50)

        # Устанавливаем минимальную ширину для остальных колонок
        for col in range(1, self.table.columnCount()):
            self.table.setColumnWidth(col, 120)

        # Настраиваем шрифт и цвет заголовков
        header_font = QFont()
        header_font.setBold(True)
        for col in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(col)
            if item:
                item.setFont(header_font)
                item.setBackground(QColor(240, 240, 240))

        # Устанавливаем выравнивание заголовков
        for col in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(col)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def check_calculation_status(self, project_code: Optional[str]) -> bool:
        """
        Проверка наличия результатов расчета
        """
        # Проверяем наличие кода проекта
        if not project_code:
            return False

        # Проверяем наличие результатов
        results = self.calc_repo.get_by_project(project_code)

        if not results:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Для проекта {project_code} не найдены результаты расчетов."
            )
            return False

        return True