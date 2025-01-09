# widgets/risk_statistics_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QGridLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List
from models.calculation_result import CalculationResult


class StatisticBox(QFrame):
    """Виджет для отображения одного статистического показателя"""

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        layout.setSpacing(2)

        # Заголовок
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(8)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Значение
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(10)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)


class RiskStatisticsWidget(QWidget):
    """Виджет для отображения статистики по рискам"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QGridLayout(self)
        layout.setSpacing(10)

        # Добавляем статистические показатели
        self.total_scenarios = StatisticBox("Всего сценариев", "0")
        layout.addWidget(self.total_scenarios, 0, 0)

        self.max_casualties = StatisticBox("Макс. погибших", "0")
        layout.addWidget(self.max_casualties, 0, 1)

        self.max_injured = StatisticBox("Макс. пострадавших", "0")
        layout.addWidget(self.max_injured, 0, 2)

        self.max_damage = StatisticBox("Макс. ущерб (млн.руб)", "0.00")
        layout.addWidget(self.max_damage, 0, 3)

        self.total_death_risk = StatisticBox("Суммарный риск гибели (чел/год)", "0.00")
        layout.addWidget(self.total_death_risk, 1, 0)

        self.total_injury_risk = StatisticBox("Суммарный риск травмирования (чел/год)", "0.00")
        layout.addWidget(self.total_injury_risk, 1, 1)

        self.max_death_frequency = StatisticBox("Макс. частота аварий с гибелью (1/год)", "0.00")
        layout.addWidget(self.max_death_frequency, 1, 2)

        self.max_eco_damage = StatisticBox("Макс. экол. ущерб (млн.руб)", "0.00")
        layout.addWidget(self.max_eco_damage, 1, 3)

    def update_statistics(self, results: List[CalculationResult]):
        """Обновление статистики на основе результатов расчета"""
        if not results:
            return

        # Обновляем показатели
        self.total_scenarios.findChildren(QLabel)[-1].setText(str(len(results)))

        max_casualties = max(r.casualties for r in results)
        self.max_casualties.findChildren(QLabel)[-1].setText(str(max_casualties))

        max_injured = max(r.injured for r in results)
        self.max_injured.findChildren(QLabel)[-1].setText(str(max_injured))

        max_damage = max(r.total_damage for r in results)
        self.max_damage.findChildren(QLabel)[-1].setText(f"{max_damage:.2f}")

        total_death_risk = sum(r.casualty_risk for r in results)
        self.total_death_risk.findChildren(QLabel)[-1].setText(f"{total_death_risk:.2e}")

        total_injury_risk = sum(r.injury_risk for r in results)
        self.total_injury_risk.findChildren(QLabel)[-1].setText(f"{total_injury_risk:.2e}")

        # Максимальная частота среди сценариев с погибшими
        death_scenarios = [r for r in results if r.casualties >= 1]
        if death_scenarios:
            max_death_frequency = max(r.probability for r in death_scenarios)
            self.max_death_frequency.findChildren(QLabel)[-1].setText(f"{max_death_frequency:.2e}")

        max_eco_damage = max(r.environmental_damage for r in results)
        self.max_eco_damage.findChildren(QLabel)[-1].setText(f"{max_eco_damage:.2f}")