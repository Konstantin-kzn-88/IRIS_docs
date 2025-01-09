# widgets/pump_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QDialogButtonBox,
                               QMessageBox, QComboBox, QLabel,
                               QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt
from models.equipment import Pump, EquipmentType
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from utilities.equipment_name_validator import validate_equipment_name

class PumpDialog(QDialog):
    """Диалог добавления/редактирования насоса"""

    def __init__(self, db: DatabaseConnection, parent=None, pump: Pump = None):
        super().__init__(parent)
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)
        self.pump = pump
        self.setup_ui()

        if pump:
            self.setWindowTitle("Редактирование насоса")
            self.load_pump_data()
        else:
            self.setWindowTitle("Добавление насоса")

        # Устанавливаем размеры диалога
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем форму
        form_layout = QFormLayout()

        # Выбор проекта
        self.project_combo = QComboBox()
        self.load_projects()
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        form_layout.addRow("Проект *:", self.project_combo)

        # Выбор вещества
        self.substance_combo = QComboBox()
        self.load_substances()
        form_layout.addRow("Вещество *:", self.substance_combo)

        # Основные поля
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите наименование в формате: Название (составляющая)")
        form_layout.addRow("Наименование *:", self.name_edit)

        # Компонент предприятия
        self.component_edit = QLineEdit()
        self.component_edit.setPlaceholderText("Например: Цех №1, Установка А и т.д.")
        form_layout.addRow("Компонент предприятия:", self.component_edit)

        # Идентификатор подсистемы
        self.sub_id_edit = QLineEdit()
        self.sub_id_edit.setPlaceholderText("Например: PUMP-001")
        form_layout.addRow("Идентификатор:", self.sub_id_edit)

        # Тип насоса
        self.pump_type_combo = QComboBox()
        self.pump_type_combo.addItems([
            "Центробежные герметичные",
            "Центробежные с уплотнениями",
            "Поршневые"
        ])
        form_layout.addRow("Тип насоса *:", self.pump_type_combo)

        # Объем
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 1000)
        self.volume_spin.setDecimals(2)
        self.volume_spin.setSuffix(" м³")
        form_layout.addRow("Объем:", self.volume_spin)

        # Давление
        self.pressure_spin = QDoubleSpinBox()
        self.pressure_spin.setRange(0, 100)
        self.pressure_spin.setDecimals(2)
        self.pressure_spin.setSuffix(" МПа")
        form_layout.addRow("Давление *:", self.pressure_spin)

        # Температура
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(-100, 1000)
        self.temperature_spin.setDecimals(1)
        self.temperature_spin.setSuffix(" °C")
        form_layout.addRow("Температура *:", self.temperature_spin)

        # Расход
        self.flow_spin = QDoubleSpinBox()
        self.flow_spin.setRange(0, 1000)
        self.flow_spin.setDecimals(2)
        self.flow_spin.setSuffix(" кг/с")
        form_layout.addRow("Расход:", self.flow_spin)

        # Время выброса
        self.time_out_spin = QDoubleSpinBox()
        self.time_out_spin.setRange(0, 3600)
        self.time_out_spin.setDecimals(1)
        self.time_out_spin.setSuffix(" с")
        form_layout.addRow("Время выброса:", self.time_out_spin)

        # Ожидаемое количество пострадавших
        self.casualties_spin = QSpinBox()
        self.casualties_spin.setRange(0, 1000)
        form_layout.addRow("Ожидаемые пострадавшие:", self.casualties_spin)

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

    def on_project_changed(self, index):
        """Обработчик изменения проекта"""
        project_id = self.project_combo.currentData()
        if project_id:
            project = self.project_repo.get_by_id(project_id)
            if project and project.project_code:
                current_name = self.name_edit.text().strip()
                # Если имя пустое или начинается со старого кода проекта
                if not current_name or (hasattr(self, '_last_project_code') and
                                        current_name.startswith(self._last_project_code)):
                    self.name_edit.setText(f"{project.project_code} - ")
                self._last_project_code = project.project_code

    def load_projects(self):
        """Загрузка списка проектов"""
        projects = self.project_repo.get_all()
        # Сортируем проекты сначала по коду проекта, затем по названию
        projects.sort(key=lambda x: (x.project_code or '', x.name))

        for project in projects:
            display_text = f"{project.project_code or '---'} | {project.name}"
            self.project_combo.addItem(display_text, userData=project.id)

    def load_substances(self):
        """Загрузка списка веществ"""
        substances = self.substance_repo.get_all()
        for substance in substances:
            self.substance_combo.addItem(substance.sub_name, userData=substance.id)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        equipment_name = self.name_edit.text().strip()
        is_valid, error_message = validate_equipment_name(equipment_name)
        if not is_valid:
            QMessageBox.warning(self, "Предупреждение", error_message)
            self.name_edit.setFocus()
            return

        if self.project_combo.currentData() is None:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите проект")
            return

        if self.substance_combo.currentData() is None:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите вещество")
            return

        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Наименование насоса не может быть пустым")
            self.name_edit.setFocus()
            return

        if self.pressure_spin.value() <= 0:
            QMessageBox.warning(self, "Предупреждение",
                                "Давление должно быть больше 0")
            self.pressure_spin.setFocus()
            return

        self.accept()

    def load_pump_data(self):
        """Загрузка данных насоса в форму"""
        # Устанавливаем проект
        index = self.project_combo.findData(self.pump.project_id)
        if index >= 0:
            self.project_combo.setCurrentIndex(index)

        # Устанавливаем вещество
        index = self.substance_combo.findData(self.pump.substance_id)
        if index >= 0:
            self.substance_combo.setCurrentIndex(index)

        self.name_edit.setText(self.pump.name)

        if self.pump.component_enterprise:
            self.component_edit.setText(self.pump.component_enterprise)

        if self.pump.sub_id:
            self.sub_id_edit.setText(self.pump.sub_id)

        # Тип насоса
        index = self.pump_type_combo.findText(self.pump.pump_type)
        if index >= 0:
            self.pump_type_combo.setCurrentIndex(index)

        if self.pump.volume is not None:
            self.volume_spin.setValue(self.pump.volume)

        self.pressure_spin.setValue(self.pump.pressure)
        self.temperature_spin.setValue(self.pump.temperature)

        if self.pump.flow is not None:
            self.flow_spin.setValue(self.pump.flow)

        if self.pump.time_out is not None:
            self.time_out_spin.setValue(self.pump.time_out)

        if self.pump.expected_casualties is not None:
            self.casualties_spin.setValue(self.pump.expected_casualties)

    def get_pump_data(self) -> Pump:
        """Получение данных насоса из формы"""
        return Pump(
            id=self.pump.id if self.pump else None,
            project_id=self.project_combo.currentData(),
            substance_id=self.substance_combo.currentData(),
            name=self.name_edit.text().strip(),
            equipment_type=EquipmentType.PUMP,
            component_enterprise=self.component_edit.text().strip() or None,
            sub_id=self.sub_id_edit.text().strip() or None,
            pressure=self.pressure_spin.value(),
            temperature=self.temperature_spin.value(),
            expected_casualties=self.casualties_spin.value(),
            pump_type=self.pump_type_combo.currentText(),
            volume=self.volume_spin.value() if self.volume_spin.value() > 0 else None,
            flow=self.flow_spin.value() if self.flow_spin.value() > 0 else None,
            time_out=self.time_out_spin.value() if self.time_out_spin.value() > 0 else None
        )