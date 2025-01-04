# widgets/substance_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QDialogButtonBox,
                               QMessageBox, QComboBox, QLabel,
                               QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt
from models.substance import Substance, SubstanceType


class SubstanceDialog(QDialog):
    """Диалог добавления/редактирования вещества"""

    def __init__(self, parent=None, substance: Substance = None):
        super().__init__(parent)
        self.substance = substance
        self.setup_ui()

        if substance:
            self.setWindowTitle("Редактирование вещества")
            self.load_substance_data()
        else:
            self.setWindowTitle("Добавление вещества")

        # Устанавливаем размеры диалога
        self.setMinimumWidth(600)
        self.setMinimumHeight(800)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем форму
        form_layout = QFormLayout()

        # Основные поля
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите наименование вещества")
        form_layout.addRow("Наименование *:", self.name_edit)

        # Класс опасности
        self.class_spin = QSpinBox()
        self.class_spin.setRange(1, 4)
        form_layout.addRow("Класс опасности *:", self.class_spin)

        # Тип вещества
        self.type_combo = QComboBox()
        for sub_type in SubstanceType:
            self.type_combo.addItem(SubstanceType.get_display_name(sub_type), userData=sub_type)
        form_layout.addRow("Тип вещества *:", self.type_combo)

        # Физические свойства
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0, 100000)
        self.density_spin.setDecimals(3)
        self.density_spin.setSuffix(" кг/м³")
        form_layout.addRow("Плотность жидкости:", self.density_spin)

        self.molecular_weight_spin = QDoubleSpinBox()
        self.molecular_weight_spin.setRange(0, 1000)
        self.molecular_weight_spin.setDecimals(3)
        self.molecular_weight_spin.setSuffix(" г/моль")
        form_layout.addRow("Молекулярная масса:", self.molecular_weight_spin)

        self.boiling_temp_spin = QDoubleSpinBox()
        self.boiling_temp_spin.setRange(-273.15, 1000)
        self.boiling_temp_spin.setDecimals(2)
        self.boiling_temp_spin.setSuffix(" °C")
        form_layout.addRow("Температура кипения:", self.boiling_temp_spin)

        self.heat_evaporation_spin = QDoubleSpinBox()
        self.heat_evaporation_spin.setRange(0, 1000000)
        self.heat_evaporation_spin.setDecimals(2)
        self.heat_evaporation_spin.setSuffix(" кДж/кг")
        form_layout.addRow("Теплота испарения:", self.heat_evaporation_spin)

        self.adiabatic_spin = QDoubleSpinBox()
        self.adiabatic_spin.setRange(1, 2)
        self.adiabatic_spin.setDecimals(3)
        form_layout.addRow("Показатель адиабаты:", self.adiabatic_spin)

        self.heat_capacity_spin = QDoubleSpinBox()
        self.heat_capacity_spin.setRange(0, 100)
        self.heat_capacity_spin.setDecimals(3)
        self.heat_capacity_spin.setSuffix(" кДж/(кг·К)")
        form_layout.addRow("Теплоемкость:", self.heat_capacity_spin)

        self.heat_combustion_spin = QDoubleSpinBox()
        self.heat_combustion_spin.setRange(0, 1000000)
        self.heat_combustion_spin.setDecimals(2)
        self.heat_combustion_spin.setSuffix(" кДж/кг")
        form_layout.addRow("Теплота сгорания:", self.heat_combustion_spin)

        # Параметры взрывоопасности
        self.sigma_combo = QComboBox()
        self.sigma_combo.addItems(["4", "7"])
        form_layout.addRow("Сигма:", self.sigma_combo)

        self.energy_level_combo = QComboBox()
        self.energy_level_combo.addItems(["1", "2"])
        form_layout.addRow("Энергетический уровень:", self.energy_level_combo)

        self.flash_point_spin = QDoubleSpinBox()
        self.flash_point_spin.setRange(-100, 500)
        self.flash_point_spin.setDecimals(2)
        self.flash_point_spin.setSuffix(" °C")
        form_layout.addRow("Температура вспышки:", self.flash_point_spin)

        self.auto_ignition_temp_spin = QDoubleSpinBox()
        self.auto_ignition_temp_spin.setRange(0, 1000)
        self.auto_ignition_temp_spin.setDecimals(2)
        self.auto_ignition_temp_spin.setSuffix(" °C")
        form_layout.addRow("Температура самовоспламенения:", self.auto_ignition_temp_spin)

        # Концентрационные пределы
        self.lower_concentration_spin = QDoubleSpinBox()
        self.lower_concentration_spin.setRange(0, 100)
        self.lower_concentration_spin.setDecimals(2)
        self.lower_concentration_spin.setSuffix(" % об.")
        form_layout.addRow("Нижний концентрационный предел:", self.lower_concentration_spin)

        self.upper_concentration_spin = QDoubleSpinBox()
        self.upper_concentration_spin.setRange(0, 100)
        self.upper_concentration_spin.setDecimals(2)
        self.upper_concentration_spin.setSuffix(" % об.")
        form_layout.addRow("Верхний концентрационный предел:", self.upper_concentration_spin)

        # Токсикологические характеристики
        self.threshold_toxic_spin = QDoubleSpinBox()
        self.threshold_toxic_spin.setRange(0, 1000000)
        self.threshold_toxic_spin.setDecimals(3)
        self.threshold_toxic_spin.setSuffix(" мг·мин/л")
        form_layout.addRow("Пороговая токсодоза:", self.threshold_toxic_spin)

        self.lethal_toxic_spin = QDoubleSpinBox()
        self.lethal_toxic_spin.setRange(0, 1000000)
        self.lethal_toxic_spin.setDecimals(3)
        self.lethal_toxic_spin.setSuffix(" мг·мин/л")
        form_layout.addRow("Смертельная токсодоза:", self.lethal_toxic_spin)

        layout.addLayout(form_layout)

        # Добавляем подсказку о обязательных полях
        layout.addWidget(QLabel("* - обязательные поля"))

        # Создаем кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Наименование вещества не может быть пустым")
            self.name_edit.setFocus()
            return

        # Проверяем концентрационные пределы
        if (self.lower_concentration_spin.value() > 0 and
                self.upper_concentration_spin.value() > 0 and
                self.lower_concentration_spin.value() >= self.upper_concentration_spin.value()):
            QMessageBox.warning(self, "Предупреждение",
                                "Нижний концентрационный предел должен быть "
                                "меньше верхнего")
            return

        self.accept()

    def load_substance_data(self):
        """Загрузка данных вещества в форму"""
        self.name_edit.setText(self.substance.sub_name)
        self.class_spin.setValue(self.substance.class_substance)

        # Устанавливаем тип вещества
        index = self.type_combo.findData(self.substance.sub_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Устанавливаем физические свойства
        if self.substance.density_liquid is not None:
            self.density_spin.setValue(self.substance.density_liquid)
        if self.substance.molecular_weight is not None:
            self.molecular_weight_spin.setValue(self.substance.molecular_weight)
        if self.substance.boiling_temperature_liquid is not None:
            self.boiling_temp_spin.setValue(self.substance.boiling_temperature_liquid)
        if self.substance.heat_evaporation_liquid is not None:
            self.heat_evaporation_spin.setValue(self.substance.heat_evaporation_liquid)
        if self.substance.adiabatic is not None:
            self.adiabatic_spin.setValue(self.substance.adiabatic)
        if self.substance.heat_capacity_liquid is not None:
            self.heat_capacity_spin.setValue(self.substance.heat_capacity_liquid)
        if self.substance.heat_of_combustion is not None:
            self.heat_combustion_spin.setValue(self.substance.heat_of_combustion)

        # Устанавливаем параметры взрывоопасности
        if self.substance.sigma is not None:
            self.sigma_combo.setCurrentText(str(self.substance.sigma))
        if self.substance.energy_level is not None:
            self.energy_level_combo.setCurrentText(str(self.substance.energy_level))
        if self.substance.flash_point is not None:
            self.flash_point_spin.setValue(self.substance.flash_point)
        if self.substance.auto_ignition_temp is not None:
            self.auto_ignition_temp_spin.setValue(self.substance.auto_ignition_temp)
        if self.substance.lower_concentration_limit is not None:
            self.lower_concentration_spin.setValue(self.substance.lower_concentration_limit)
        if self.substance.upper_concentration_limit is not None:
            self.upper_concentration_spin.setValue(self.substance.upper_concentration_limit)
        if self.substance.threshold_toxic_dose is not None:
            self.threshold_toxic_spin.setValue(self.substance.threshold_toxic_dose)
        if self.substance.lethal_toxic_dose is not None:
            self.lethal_toxic_spin.setValue(self.substance.lethal_toxic_dose)

    def get_substance_data(self) -> Substance:
        """Получение данных вещества из формы"""
        return Substance(
            id=self.substance.id if self.substance else None,
            sub_name=self.name_edit.text().strip(),
            class_substance=self.class_spin.value(),
            sub_type=self.type_combo.currentData(),
            density_liquid=self.density_spin.value() if self.density_spin.value() > 0 else None,
            molecular_weight=self.molecular_weight_spin.value() if self.molecular_weight_spin.value() > 0 else None,
            boiling_temperature_liquid=self.boiling_temp_spin.value(),
            heat_evaporation_liquid=self.heat_evaporation_spin.value() if self.heat_evaporation_spin.value() > 0 else None,
            adiabatic=self.adiabatic_spin.value(),
            heat_capacity_liquid=self.heat_capacity_spin.value() if self.heat_capacity_spin.value() > 0 else None,
            heat_of_combustion=self.heat_combustion_spin.value() if self.heat_combustion_spin.value() > 0 else None,
            sigma=int(self.sigma_combo.currentText()),
            energy_level=int(self.energy_level_combo.currentText()),
            flash_point=self.flash_point_spin.value(),
            auto_ignition_temp=self.auto_ignition_temp_spin.value() if self.auto_ignition_temp_spin.value() > 0 else None,
            lower_concentration_limit=self.lower_concentration_spin.value() if self.lower_concentration_spin.value() > 0 else None,
            upper_concentration_limit=self.upper_concentration_spin.value() if self.upper_concentration_spin.value() > 0 else None,
            threshold_toxic_dose=self.threshold_toxic_spin.value() if self.threshold_toxic_spin.value() > 0 else None,
            lethal_toxic_dose=self.lethal_toxic_spin.value() if self.lethal_toxic_spin.value() > 0 else None
        )