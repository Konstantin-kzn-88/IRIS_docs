# widgets/organization_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QDateEdit, QDialogButtonBox,
                               QMessageBox, QComboBox, QLabel)
from PySide6.QtCore import Qt, QDate
from models.organization import Organization
from datetime import datetime


class OrganizationDialog(QDialog):
    """Диалог добавления/редактирования организации"""

    def __init__(self, parent=None, organization: Organization = None):
        super().__init__(parent)
        self.organization = organization
        self.setup_ui()
        if organization:
            self.setWindowTitle("Редактирование организации")
            self.load_organization_data()
        else:
            self.setWindowTitle("Добавление организации")

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
        self.name_edit.setPlaceholderText("Введите краткое наименование")
        form_layout.addRow("Наименование *:", self.name_edit)

        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Введите полное наименование")
        form_layout.addRow("Полное наименование *:", self.full_name_edit)

        self.org_form_combo = QComboBox()
        self.org_form_combo.addItems([
            "ООО", "АО", "ПАО", "ЗАО", "ИП",
            "ФГУП", "ГУП", "МУП", "Другое"
        ])
        form_layout.addRow("Форма собственности *:", self.org_form_combo)

        self.head_position_edit = QLineEdit()
        self.head_position_edit.setPlaceholderText("Например: Генеральный директор")
        form_layout.addRow("Должность руководителя:", self.head_position_edit)

        self.head_name_edit = QLineEdit()
        self.head_name_edit.setPlaceholderText("Фамилия Имя Отчество")
        form_layout.addRow("ФИО руководителя:", self.head_name_edit)

        self.legal_address_edit = QLineEdit()
        self.legal_address_edit.setPlaceholderText("Полный юридический адрес")
        form_layout.addRow("Юридический адрес:", self.legal_address_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        form_layout.addRow("Телефон:", self.phone_edit)

        self.fax_edit = QLineEdit()
        self.fax_edit.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        form_layout.addRow("Факс:", self.fax_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@domain.com")
        form_layout.addRow("Email:", self.email_edit)

        self.license_number_edit = QLineEdit()
        self.license_number_edit.setPlaceholderText("Номер лицензии")
        form_layout.addRow("Номер лицензии:", self.license_number_edit)

        self.license_date_edit = QDateEdit()
        self.license_date_edit.setCalendarPopup(True)
        self.license_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Дата лицензии:", self.license_date_edit)

        # Дополнительные поля
        self.ind_safety_system_edit = QLineEdit()
        self.ind_safety_system_edit.setPlaceholderText("Описание системы промышленной безопасности")
        form_layout.addRow("Система ПБ:", self.ind_safety_system_edit)

        self.prod_control_edit = QLineEdit()
        self.prod_control_edit.setPlaceholderText("Описание производственного контроля")
        form_layout.addRow("Производственный контроль:", self.prod_control_edit)

        self.accident_investigation_edit = QLineEdit()
        self.accident_investigation_edit.setPlaceholderText("Порядок расследования аварий")
        form_layout.addRow("Расследование аварий:", self.accident_investigation_edit)

        self.rescue_contract_edit = QLineEdit()
        self.rescue_contract_edit.setPlaceholderText("Номер договора")
        form_layout.addRow("Договор со спасателями:", self.rescue_contract_edit)

        self.rescue_certificate_edit = QLineEdit()
        self.rescue_certificate_edit.setPlaceholderText("Номер свидетельства")
        form_layout.addRow("Свидетельство спасателей:", self.rescue_certificate_edit)

        self.fire_contract_edit = QLineEdit()
        self.fire_contract_edit.setPlaceholderText("Номер договора")
        form_layout.addRow("Договор с пожарными:", self.fire_contract_edit)

        self.emergency_certificate_edit = QLineEdit()
        self.emergency_certificate_edit.setPlaceholderText("Номер свидетельства")
        form_layout.addRow("Свидетельство НАСФ:", self.emergency_certificate_edit)

        self.material_reserves_edit = QLineEdit()
        self.material_reserves_edit.setPlaceholderText("Описание материальных резервов")
        form_layout.addRow("Материальные резервы:", self.material_reserves_edit)

        self.financial_reserves_edit = QLineEdit()
        self.financial_reserves_edit.setPlaceholderText("Описание финансовых резервов")
        form_layout.addRow("Финансовые резервы:", self.financial_reserves_edit)

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
                                "Наименование организации не может быть пустым")
            self.name_edit.setFocus()
            return

        if not self.full_name_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Полное наименование организации не может быть пустым")
            self.full_name_edit.setFocus()
            return

        # Проверяем формат email если он указан
        email = self.email_edit.text().strip()
        if email and '@' not in email:
            QMessageBox.warning(self, "Предупреждение",
                                "Указан некорректный email адрес")
            self.email_edit.setFocus()
            return

        # Проверяем формат телефона если он указан
        phone = self.phone_edit.text().strip()
        if phone and not (phone.startswith('+7') or phone.startswith('8')):
            QMessageBox.warning(self, "Предупреждение",
                                "Телефон должен начинаться с +7 или 8")
            self.phone_edit.setFocus()
            return

        self.accept()

    def load_organization_data(self):
        """Загрузка данных организации в форму"""
        self.name_edit.setText(self.organization.name)
        self.full_name_edit.setText(self.organization.full_name)

        # Находим индекс формы собственности в комбобоксе
        index = self.org_form_combo.findText(self.organization.org_form)
        if index >= 0:
            self.org_form_combo.setCurrentIndex(index)

        if self.organization.head_position:
            self.head_position_edit.setText(self.organization.head_position)
        if self.organization.head_name:
            self.head_name_edit.setText(self.organization.head_name)
        if self.organization.legal_address:
            self.legal_address_edit.setText(self.organization.legal_address)
        if self.organization.phone:
            self.phone_edit.setText(self.organization.phone)
        if self.organization.fax:
            self.fax_edit.setText(self.organization.fax)
        if self.organization.email:
            self.email_edit.setText(self.organization.email)
        if self.organization.license_number:
            self.license_number_edit.setText(self.organization.license_number)
        if self.organization.license_date:
            self.license_date_edit.setDate(QDate(
                self.organization.license_date.year,
                self.organization.license_date.month,
                self.organization.license_date.day
            ))
        if self.organization.ind_safety_system:
            self.ind_safety_system_edit.setText(self.organization.ind_safety_system)
        if self.organization.prod_control:
            self.prod_control_edit.setText(self.organization.prod_control)
        if self.organization.accident_investigation:
            self.accident_investigation_edit.setText(self.organization.accident_investigation)
        if self.organization.rescue_contract:
            self.rescue_contract_edit.setText(self.organization.rescue_contract)
        if self.organization.rescue_certificate:
            self.rescue_certificate_edit.setText(self.organization.rescue_certificate)
        if self.organization.fire_contract:
            self.fire_contract_edit.setText(self.organization.fire_contract)
        if self.organization.emergency_certificate:
            self.emergency_certificate_edit.setText(self.organization.emergency_certificate)
        if self.organization.material_reserves:
            self.material_reserves_edit.setText(self.organization.material_reserves)
        if self.organization.financial_reserves:
            self.financial_reserves_edit.setText(self.organization.financial_reserves)

    def get_organization_data(self) -> Organization:
        """Получение данных организации из формы"""
        license_date = self.license_date_edit.date().toPython()

        return Organization(
            id=self.organization.id if self.organization else None,
            name=self.name_edit.text().strip(),
            full_name=self.full_name_edit.text().strip(),
            org_form=self.org_form_combo.currentText(),
            head_position=self.head_position_edit.text().strip() or None,
            head_name=self.head_name_edit.text().strip() or None,
            legal_address=self.legal_address_edit.text().strip() or None,
            phone=self.phone_edit.text().strip() or None,
            fax=self.fax_edit.text().strip() or None,
            email=self.email_edit.text().strip() or None,
            license_number=self.license_number_edit.text().strip() or None,
            license_date=license_date,
            ind_safety_system=self.ind_safety_system_edit.text().strip() or None,
            prod_control=self.prod_control_edit.text().strip() or None,
            accident_investigation=self.accident_investigation_edit.text().strip() or None,
            rescue_contract=self.rescue_contract_edit.text().strip() or None,
            rescue_certificate=self.rescue_certificate_edit.text().strip() or None,
            fire_contract=self.fire_contract_edit.text().strip() or None,
            emergency_certificate=self.emergency_certificate_edit.text().strip() or None,
            material_reserves=self.material_reserves_edit.text().strip() or None,
            financial_reserves=self.financial_reserves_edit.text().strip() or None
        )