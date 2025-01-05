# calculation_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                               QComboBox, QPushButton, QMessageBox,
                               QDialogButtonBox)
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from calculation_manager import CalculationManager


class CalculationDialog(QDialog):
    """Диалог для запуска расчета"""

    def __init__(self, db: DatabaseConnection, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.calculation_manager = CalculationManager(db)

        self.setWindowTitle("Расчет сценария С1")
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем форму
        form_layout = QFormLayout()

        # Выбор проекта
        self.project_combo = QComboBox()
        self.load_projects()
        form_layout.addRow("Проект:", self.project_combo)

        layout.addLayout(form_layout)

        # Создаем кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.run_calculation)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_projects(self):
        """Загрузка списка проектов"""
        projects = self.project_repo.get_all()
        # Сортируем проекты по коду
        projects.sort(key=lambda x: (x.project_code or '', x.name))

        for project in projects:
            if project.project_code:  # Только проекты с кодом
                display_text = f"{project.project_code} | {project.name}"
                self.project_combo.addItem(display_text, userData=project.project_code)

    def run_calculation(self):
        """Запуск расчета"""
        project_code = self.project_combo.currentData()
        if not project_code:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите проект")
            return

        try:
            self.calculation_manager.create_initial_calculation(project_code)
            QMessageBox.information(self, "Информация",
                                    "Расчет успешно выполнен")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось выполнить расчет: {str(e)}")