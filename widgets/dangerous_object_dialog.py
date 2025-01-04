# widgets/dangerous_object_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QDialogButtonBox,
                               QMessageBox, QComboBox, QSpinBox, QLabel)
from PySide6.QtCore import Qt
from models.dangerous_object import DangerousObject, HazardClass
from database.db_connection import DatabaseConnection
from database.repositories.organization_repo import OrganizationRepository


class DangerousObjectDialog(QDialog):
    """Диалог добавления/редактирования ОПО"""

    def __init__(self, db: DatabaseConnection, parent=None, dangerous_object: DangerousObject = None):
        super().__init__(parent)
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.dangerous_object = dangerous_object
        self.setup_ui()

        if dangerous_object:
            self.setWindowTitle("Редактирование ОПО")
            self.load_object_data()
        else:
            self.setWindowTitle("Добавление ОПО")

        # Устанавливаем размеры диалога
        self.setMinimumWidth(500)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем форму
        form_layout = QFormLayout()

        # Выбор организации
        self.org_combo = QComboBox()
        self.load_organizations()
        form_layout.addRow("Организация *:", self.org_combo)

        # Основные поля
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите наименование ОПО")
        form_layout.addRow("Наименование *:", self.name_edit)

        self.reg_number_edit = QLineEdit()
        self.reg_number_edit.setPlaceholderText("АХХ-ХХХХХ-ХХХХ")
        form_layout.addRow("Рег. номер *:", self.reg_number_edit)

        # Класс опасности
        self.hazard_class_combo = QComboBox()
        self.hazard_class_combo.addItems([
            HazardClass.get_display_name(HazardClass.CLASS_I),
            HazardClass.get_display_name(HazardClass.CLASS_II),
            HazardClass.get_display_name(HazardClass.CLASS_III),
            HazardClass.get_display_name(HazardClass.CLASS_IV)
        ])
        form_layout.addRow("Класс опасности *:", self.hazard_class_combo)

        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Адрес местонахождения ОПО")
        form_layout.addRow("Местоположение *:", self.location_edit)

        self.employee_count_spin = QSpinBox()
        self.employee_count_spin.setMinimum(1)
        self.employee_count_spin.setMaximum(99999)
        form_layout.addRow("Количество сотрудников *:", self.employee_count_spin)

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

    def load_organizations(self):
        """Загрузка списка организаций"""
        organizations = self.org_repo.get_all()
        self.org_combo.clear()
        for org in organizations:
            self.org_combo.addItem(org.name, userData=org.id)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        if self.org_combo.currentData() is None:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите организацию")
            return

        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Наименование ОПО не может быть пустым")
            self.name_edit.setFocus()
            return

        if not self.reg_number_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Регистрационный номер не может быть пустым")
            self.reg_number_edit.setFocus()
            return

        if not self.location_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Местоположение не может быть пустым")
            self.location_edit.setFocus()
            return

        # Проверяем формат регистрационного номера
        import re
        reg_pattern = r'^[А-Я]\d{2}-\d{5}-\d{4}$'
        if not re.match(reg_pattern, self.reg_number_edit.text().strip()):
            QMessageBox.warning(self, "Предупреждение",
                                "Неверный формат регистрационного номера\n"
                                "Формат: АХХ-ХХХХХ-ХХХХ")
            self.reg_number_edit.setFocus()
            return

        self.accept()

    def load_object_data(self):
        """Загрузка данных ОПО в форму"""
        # Устанавливаем организацию
        index = self.org_combo.findData(self.dangerous_object.organization_id)
        if index >= 0:
            self.org_combo.setCurrentIndex(index)

        self.name_edit.setText(self.dangerous_object.name)
        self.reg_number_edit.setText(self.dangerous_object.reg_number)

        # Устанавливаем класс опасности
        hazard_class_name = HazardClass.get_display_name(self.dangerous_object.hazard_class)
        index = self.hazard_class_combo.findText(hazard_class_name)
        if index >= 0:
            self.hazard_class_combo.setCurrentIndex(index)

        self.location_edit.setText(self.dangerous_object.location)
        self.employee_count_spin.setValue(self.dangerous_object.employee_count)

    def get_object_data(self) -> DangerousObject:
        """Получение данных ОПО из формы"""
        # Преобразуем отображаемое имя класса опасности в enum
        hazard_class_name = self.hazard_class_combo.currentText()
        hazard_class = next(cls for cls in HazardClass
                            if HazardClass.get_display_name(cls) == hazard_class_name)

        return DangerousObject(
            id=self.dangerous_object.id if self.dangerous_object else None,
            organization_id=self.org_combo.currentData(),
            name=self.name_edit.text().strip(),
            reg_number=self.reg_number_edit.text().strip(),
            hazard_class=hazard_class,
            location=self.location_edit.text().strip(),
            employee_count=self.employee_count_spin.value()
        )