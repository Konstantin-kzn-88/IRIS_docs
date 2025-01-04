# widgets/project_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QLineEdit, QDialogButtonBox,
                               QMessageBox, QComboBox, QLabel,
                               QTextEdit)
from PySide6.QtCore import Qt
from models.project import Project
from database.db_connection import DatabaseConnection
from database.repositories.dangerous_object_repo import DangerousObjectRepository


class ProjectDialog(QDialog):
    """Диалог добавления/редактирования проекта"""

    def __init__(self, db: DatabaseConnection, parent=None, project: Project = None):
        super().__init__(parent)
        self.db = db
        self.opo_repo = DangerousObjectRepository(db)
        self.project = project
        self.setup_ui()

        if project:
            self.setWindowTitle("Редактирование проекта")
            self.load_project_data()
        else:
            self.setWindowTitle("Добавление проекта")

        # Устанавливаем размеры диалога
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем форму
        form_layout = QFormLayout()

        # Выбор ОПО
        self.opo_combo = QComboBox()
        self.load_dangerous_objects()
        form_layout.addRow("ОПО *:", self.opo_combo)

        # Основные поля
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите наименование проекта")
        form_layout.addRow("Наименование *:", self.name_edit)

        # Поле для описания
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Введите описание проекта")
        self.description_edit.setMinimumHeight(100)
        form_layout.addRow("Описание:", self.description_edit)

        # Описание автоматизации
        self.automation_edit = QTextEdit()
        self.automation_edit.setPlaceholderText("Введите описание автоматизации")
        self.automation_edit.setMinimumHeight(100)
        form_layout.addRow("Описание автоматизации:", self.automation_edit)

        # Шифры проекта
        self.project_code_edit = QLineEdit()
        self.project_code_edit.setPlaceholderText("Введите шифр проекта")
        form_layout.addRow("Шифр проекта:", self.project_code_edit)

        self.dpb_code_edit = QLineEdit()
        self.dpb_code_edit.setPlaceholderText("Введите шифр ДПБ")
        form_layout.addRow("Шифр ДПБ:", self.dpb_code_edit)

        self.rpz_code_edit = QLineEdit()
        self.rpz_code_edit.setPlaceholderText("Введите шифр РПЗ")
        form_layout.addRow("Шифр РПЗ:", self.rpz_code_edit)

        self.ifl_code_edit = QLineEdit()
        self.ifl_code_edit.setPlaceholderText("Введите шифр ИФЛ")
        form_layout.addRow("Шифр ИФЛ:", self.ifl_code_edit)

        self.gochs_code_edit = QLineEdit()
        self.gochs_code_edit.setPlaceholderText("Введите шифр ГОЧС")
        form_layout.addRow("Шифр ГОЧС:", self.gochs_code_edit)

        self.mpb_code_edit = QLineEdit()
        self.mpb_code_edit.setPlaceholderText("Введите шифр МПБ")
        form_layout.addRow("Шифр МПБ:", self.mpb_code_edit)

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

    def load_dangerous_objects(self):
        """Загрузка списка ОПО"""
        dangerous_objects = self.opo_repo.get_all()
        self.opo_combo.clear()
        for obj in dangerous_objects:
            self.opo_combo.addItem(obj.name, userData=obj.id)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        if self.opo_combo.currentData() is None:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите ОПО")
            return

        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Предупреждение",
                                "Наименование проекта не может быть пустым")
            self.name_edit.setFocus()
            return

        self.accept()

    def load_project_data(self):
        """Загрузка данных проекта в форму"""
        # Устанавливаем ОПО
        index = self.opo_combo.findData(self.project.opo_id)
        if index >= 0:
            self.opo_combo.setCurrentIndex(index)

        self.name_edit.setText(self.project.name)

        if self.project.description:
            self.description_edit.setText(self.project.description)

        if self.project.automation_description:
            self.automation_edit.setText(self.project.automation_description)

        if self.project.project_code:
            self.project_code_edit.setText(self.project.project_code)

        if self.project.dpb_code:
            self.dpb_code_edit.setText(self.project.dpb_code)

        if self.project.rpz_code:
            self.rpz_code_edit.setText(self.project.rpz_code)

        if self.project.ifl_code:
            self.ifl_code_edit.setText(self.project.ifl_code)

        if self.project.gochs_code:
            self.gochs_code_edit.setText(self.project.gochs_code)

        if self.project.mpb_code:
            self.mpb_code_edit.setText(self.project.mpb_code)

    def get_project_data(self) -> Project:
        """Получение данных проекта из формы"""
        return Project(
            id=self.project.id if self.project else None,
            opo_id=self.opo_combo.currentData(),
            name=self.name_edit.text().strip(),
            description=self.description_edit.toPlainText().strip() or None,
            automation_description=self.automation_edit.toPlainText().strip() or None,
            project_code=self.project_code_edit.text().strip() or None,
            dpb_code=self.dpb_code_edit.text().strip() or None,
            rpz_code=self.rpz_code_edit.text().strip() or None,
            ifl_code=self.ifl_code_edit.text().strip() or None,
            gochs_code=self.gochs_code_edit.text().strip() or None,
            mpb_code=self.mpb_code_edit.text().strip() or None
        )