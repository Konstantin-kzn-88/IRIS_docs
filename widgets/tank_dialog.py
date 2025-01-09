# widgets/tank_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QLineEdit, QDialogButtonBox,
                             QMessageBox, QComboBox, QLabel,
                             QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt
from models.equipment import Tank, EquipmentType
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from utilities.equipment_name_validator import validate_equipment_name


class TankDialog(QDialog):
    """Диалог добавления/редактирования резервуара"""

    def __init__(self, db: DatabaseConnection, parent=None, tank: Tank = None):
        super().__init__(parent)
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)
        self.tank = tank
        self.setup_ui()

        if tank:
            self.setWindowTitle("Редактирование резервуара")
            self.load_tank_data()
        else:
            self.setWindowTitle("Добавление резервуара")

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
        self.sub_id_edit.setPlaceholderText("Например: TNK-001")
        form_layout.addRow("Идентификатор:", self.sub_id_edit)

        # Тип резервуара
        self.tank_type_combo = QComboBox()
        self.tank_type_combo.addItems([
            "Одностенный",
            "С внешней защитной оболочкой",
            "С двойной оболочкой",
            "Полной герметизации"
        ])
        form_layout.addRow("Тип резервуара *:", self.tank_type_combo)

        # Объем
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 100000)
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

        # Степень заполнения
        self.filling_spin = QDoubleSpinBox()
        self.filling_spin.setRange(0, 1)
        self.filling_spin.setDecimals(2)
        self.filling_spin.setSingleStep(0.05)
        self.filling_spin.setSuffix("")
        self.filling_spin.setSpecialValueText("Не задана")
        form_layout.addRow("Степень заполнения:", self.filling_spin)

        # Площадь пролива
        self.spill_spin = QDoubleSpinBox()
        self.spill_spin.setRange(0, 10000)
        self.spill_spin.setDecimals(2)
        self.spill_spin.setSuffix(" м²")
        self.spill_spin.setSpecialValueText("Не задана")
        form_layout.addRow("Площадь пролива:", self.spill_spin)

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
                              "Наименование резервуара не может быть пустым")
            self.name_edit.setFocus()
            return

        if self.pressure_spin.value() <= 0:
            QMessageBox.warning(self, "Предупреждение",
                              "Давление должно быть больше 0")
            self.pressure_spin.setFocus()
            return

        if self.volume_spin.value() > 0 and self.filling_spin.value() > 0:
            if self.spill_spin.value() <= 0:
                QMessageBox.warning(self, "Предупреждение",
                                  "При заданном объеме и степени заполнения "
                                  "необходимо указать площадь пролива")
                self.spill_spin.setFocus()
                return

        self.accept()

    def load_tank_data(self):
        """Загрузка данных резервуара в форму"""
        # Устанавливаем проект
        index = self.project_combo.findData(self.tank.project_id)
        if index >= 0:
            self.project_combo.setCurrentIndex(index)

        # Устанавливаем вещество
        index = self.substance_combo.findData(self.tank.substance_id)
        if index >= 0:
            self.substance_combo.setCurrentIndex(index)

        self.name_edit.setText(self.tank.name)

        if self.tank.component_enterprise:
            self.component_edit.setText(self.tank.component_enterprise)

        if self.tank.sub_id:
            self.sub_id_edit.setText(self.tank.sub_id)

        # Тип резервуара
        index = self.tank_type_combo.findText(self.tank.tank_type)
        if index >= 0:
            self.tank_type_combo.setCurrentIndex(index)

        if self.tank.volume is not None:
            self.volume_spin.setValue(self.tank.volume)

        self.pressure_spin.setValue(self.tank.pressure)
        self.temperature_spin.setValue(self.tank.temperature)

        if self.tank.degree_filling is not None:
            self.filling_spin.setValue(self.tank.degree_filling)

        if self.tank.spill_square is not None:
            self.spill_spin.setValue(self.tank.spill_square)

        if self.tank.expected_casualties is not None:
            self.casualties_spin.setValue(self.tank.expected_casualties)

    def get_tank_data(self) -> Tank:
        """Получение данных резервуара из формы"""
        return Tank(
            id=self.tank.id if self.tank else None,
            project_id=self.project_combo.currentData(),
            substance_id=self.substance_combo.currentData(),
            name=self.name_edit.text().strip(),
            equipment_type=EquipmentType.TANK,
            component_enterprise=self.component_edit.text().strip() or None,
            sub_id=self.sub_id_edit.text().strip() or None,
            pressure=self.pressure_spin.value(),
            temperature=self.temperature_spin.value(),
            expected_casualties=self.casualties_spin.value(),
            tank_type=self.tank_type_combo.currentText(),
            volume=self.volume_spin.value() if self.volume_spin.value() > 0 else None,
            degree_filling=self.filling_spin.value() if self.filling_spin.value() > 0 else None,
            spill_square=self.spill_spin.value() if self.spill_spin.value() > 0 else None
        )