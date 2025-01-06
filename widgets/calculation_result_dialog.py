# widgets/calculation_result_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QDialogButtonBox, QLabel, QTabWidget,
                               QWidget, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt
from models.calculation_result import CalculationResult
from models.equipment import EquipmentType
from models.substance import SubstanceType


class CalculationResultDialog(QDialog):
    """Диалог просмотра результата расчета"""

    def __init__(self, result: CalculationResult, parent=None):
        super().__init__(parent)
        self.result = result
        self.setup_ui()
        self.setWindowTitle(f"Результат расчета {result.project_code} - C{result.scenario_number}")

        # Устанавливаем размеры диалога
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем вкладки
        tab_widget = QTabWidget()

        # Основная информация
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "Основная информация")
        self.setup_main_tab(main_tab)

        # Параметры поражения
        damage_tab = QWidget()
        tab_widget.addTab(damage_tab, "Параметры поражения")
        self.setup_damage_tab(damage_tab)

        # Параметры ущерба
        loss_tab = QWidget()
        tab_widget.addTab(loss_tab, "Параметры ущерба")
        self.setup_loss_tab(loss_tab)

        # Добавляем вкладки в layout
        layout.addWidget(tab_widget)

        # Создаем кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def setup_main_tab(self, tab: QWidget):
        """Настройка вкладки основной информации"""
        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Создаем контейнер для содержимого
        content = QWidget()
        scroll_layout = QVBoxLayout(content)

        # Группа общей информации
        general_group = QGroupBox("Общая информация")
        form = QFormLayout()

        form.addRow("Код проекта:", QLabel(self.result.project_code))
        form.addRow("Номер сценария:", QLabel(f"C{self.result.scenario_number}"))
        form.addRow("Наименование оборудования:", QLabel(self.result.equipment_name))
        form.addRow("Тип оборудования:",
                    QLabel(EquipmentType.get_display_name(self.result.equipment_type)))
        form.addRow("Тип вещества:",
                    QLabel(SubstanceType.get_display_name(self.result.substance_type)))

        general_group.setLayout(form)
        scroll_layout.addWidget(general_group)

        # Группа риска
        risk_group = QGroupBox("Параметры риска")
        form = QFormLayout()

        form.addRow("Количество погибших:", QLabel(str(self.result.casualties)))
        form.addRow("Количество пострадавших:", QLabel(str(self.result.injured)))
        form.addRow("Риск гибели:", QLabel(f"{self.result.casualty_risk:.2e}"))
        form.addRow("Риск травмирования:", QLabel(f"{self.result.injury_risk:.2e}"))

        risk_group.setLayout(form)
        scroll_layout.addWidget(risk_group)

        scroll_layout.addStretch()
        scroll.setWidget(content)

        # Добавляем scroll area в tab
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)

    def setup_damage_tab(self, tab: QWidget):
        """Настройка вкладки параметров поражения"""
        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Создаем контейнер для содержимого
        content = QWidget()
        scroll_layout = QVBoxLayout(content)

        # Группа теплового излучения
        heat_group = QGroupBox("Тепловое излучение")
        form = QFormLayout()

        form.addRow("10.5 кВт/м²:", QLabel(f"{self.result.q_10_5:.2f}"))
        form.addRow("7.0 кВт/м²:", QLabel(f"{self.result.q_7_0:.2f}"))
        form.addRow("4.2 кВт/м²:", QLabel(f"{self.result.q_4_2:.2f}"))
        form.addRow("1.4 кВт/м²:", QLabel(f"{self.result.q_1_4:.2f}"))

        heat_group.setLayout(form)
        scroll_layout.addWidget(heat_group)

        # Группа избыточного давления
        pressure_group = QGroupBox("Избыточное давление")
        form = QFormLayout()

        form.addRow("53 кПа:", QLabel(f"{self.result.p_53:.2f}"))
        form.addRow("28 кПа:", QLabel(f"{self.result.p_28:.2f}"))
        form.addRow("12 кПа:", QLabel(f"{self.result.p_12:.2f}"))
        form.addRow("5 кПа:", QLabel(f"{self.result.p_5:.2f}"))
        form.addRow("2 кПа:", QLabel(f"{self.result.p_2:.2f}"))

        pressure_group.setLayout(form)
        scroll_layout.addWidget(pressure_group)

        # Группа прочих параметров
        other_group = QGroupBox("Прочие параметры")
        form = QFormLayout()

        form.addRow("Длина факела:", QLabel(f"{self.result.l_f:.2f}"))
        form.addRow("Диаметр факела:", QLabel(f"{self.result.d_f:.2f}"))
        form.addRow("Радиус НКПР:", QLabel(f"{self.result.r_nkpr:.2f}"))
        form.addRow("Радиус вспышки:", QLabel(f"{self.result.r_flash:.2f}"))
        form.addRow("Глубина поражения:", QLabel(f"{self.result.l_pt:.2f}"))
        form.addRow("Ширина поражения:", QLabel(f"{self.result.p_pt:.2f}"))
        form.addRow("Площадь пролива:", QLabel(f"{self.result.s_spill:.2f}"))

        other_group.setLayout(form)
        scroll_layout.addWidget(other_group)

        # Группа тротилового эквивалента
        tnt_group = QGroupBox("Тротиловый эквивалент")
        form = QFormLayout()

        form.addRow("600 кПа:", QLabel(f"{self.result.q_600:.2f}"))
        form.addRow("320 кПа:", QLabel(f"{self.result.q_320:.2f}"))
        form.addRow("220 кПа:", QLabel(f"{self.result.q_220:.2f}"))
        form.addRow("120 кПа:", QLabel(f"{self.result.q_120:.2f}"))

        tnt_group.setLayout(form)
        scroll_layout.addWidget(tnt_group)

        scroll_layout.addStretch()
        scroll.setWidget(content)

        # Добавляем scroll area в tab
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)

    def setup_loss_tab(self, tab: QWidget):
        """Настройка вкладки параметров ущерба"""
        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Создаем контейнер для содержимого
        content = QWidget()
        scroll_layout = QVBoxLayout(content)

        # Группа статистических показателей (добавим новую группу)
        stats_group = QGroupBox("Статистические показатели")
        form = QFormLayout()

        # Добавляем вероятность в начало группы статистических показателей
        form.addRow("Вероятность:", QLabel(f"{self.result.probability:.2e}"))

        # Существующие показатели риска
        form.addRow("Риск гибели:", QLabel(f"{self.result.casualty_risk:.2e}"))
        form.addRow("Риск травмирования:", QLabel(f"{self.result.injury_risk:.2e}"))
        form.addRow("Ожидаемый ущерб:", QLabel(f"{self.result.expected_damage:.2f} млн.руб/год"))

        stats_group.setLayout(form)
        scroll_layout.addWidget(stats_group)

        # Существующая группа потерь
        loss_group = QGroupBox("Параметры ущерба")
        form = QFormLayout()

        form.addRow("Прямые потери:",
                    QLabel(f"{self.result.direct_losses:.2f} млн.руб"))
        form.addRow("Затраты на ликвидацию:",
                    QLabel(f"{self.result.liquidation_costs:.2f} млн.руб"))
        form.addRow("Социальные потери:",
                    QLabel(f"{self.result.social_losses:.2f} млн.руб"))
        form.addRow("Косвенный ущерб:",
                    QLabel(f"{self.result.indirect_damage:.2f} млн.руб"))
        form.addRow("Экологический ущерб:",
                    QLabel(f"{self.result.environmental_damage:.2f} млн.руб"))
        form.addRow("Суммарный ущерб:",
                    QLabel(f"{self.result.total_damage:.2f} млн.руб"))

        loss_group.setLayout(form)
        scroll_layout.addWidget(loss_group)

        scroll_layout.addStretch()
        scroll.setWidget(content)

        # Добавляем scroll area в tab
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)