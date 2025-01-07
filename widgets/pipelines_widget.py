# widgets/pipelines_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QLineEdit,
                             QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from models.equipment import Pipeline, EquipmentType
from .pipeline_dialog import PipelineDialog


class PipelinesWidget(QWidget):
    """Виджет для отображения и управления списком трубопроводов"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = EquipmentRepository(db)
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем основной layout
        layout = QVBoxLayout(self)

        # Создаем панель фильтров
        filter_layout = QHBoxLayout()

        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или коду проекта...")
        self.search_input.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_input)

        # Фильтр по проекту
        filter_layout.addWidget(QLabel("Проект:"))
        self.project_filter = QComboBox()
        self.project_filter.addItem("Все")
        self.load_projects()
        self.project_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.project_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Код проекта", "Название",
            "Проект", "Длина (м)",
            "Диаметр (мм)", "Расход (кг/с)", "Давление (МПа)", "Доля авар.уч-ка."
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Создаем панель с кнопками
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.on_add)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.on_edit)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

    def load_projects(self):
        """Загрузка списка проектов в фильтр"""
        projects = self.project_repo.get_all()
        for project in projects:
            display_text = f"{project.project_code} - {project.name}" if project.project_code else project.name
            self.project_filter.addItem(display_text, userData=project.id)

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Получаем выбранные фильтры
        project_id = self.project_filter.currentData()
        search_text = self.search_input.text().strip()

        # Получаем все трубопроводы
        all_equipment = self.repo.get_by_type(EquipmentType.PIPELINE)
        pipelines = [eq for eq in all_equipment if isinstance(eq, Pipeline)]

        # Применяем фильтры
        filtered_pipelines = []
        for pipeline in pipelines:
            # Получаем проект
            project = self.project_repo.get_by_id(pipeline.project_id)
            if not project:
                continue

            # Применяем фильтр по проекту
            if project_id and pipeline.project_id != project_id:
                continue

            # Применяем текстовый поиск
            if search_text:
                search_lower = search_text.lower()
                project_code = project.project_code or ""
                if not (search_lower in pipeline.name.lower() or
                       search_lower in project_code.lower()):
                    continue

            filtered_pipelines.append((pipeline, project))

        # Заполняем таблицу
        self.table.setRowCount(len(filtered_pipelines))

        for i, (pipeline, project) in enumerate(filtered_pipelines):
            # ID
            item = QTableWidgetItem(str(pipeline.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Код проекта
            item = QTableWidgetItem(project.project_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Название
            item = QTableWidgetItem(pipeline.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Проект
            item = QTableWidgetItem(project.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Длина
            item = QTableWidgetItem(f"{pipeline.length_meters:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Диаметр
            item = QTableWidgetItem(f"{pipeline.diameter_pipeline:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Расход
            flow = "-" if pipeline.flow is None else f"{pipeline.flow:.2f}"
            item = QTableWidgetItem(flow)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

            # Давление
            item = QTableWidgetItem(f"{pipeline.pressure:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

            # Доля участка:
            item = QTableWidgetItem(f"{pipeline.accident_rate:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 8, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_pipeline_id(self) -> int:
        """Получение ID выбранного трубопровода"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления трубопровода"""
        dialog = PipelineDialog(self.db, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                pipeline = dialog.get_pipeline_data()
                self.repo.create(pipeline)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Трубопровод успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось добавить трубопровод: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования трубопровода"""
        pipeline_id = self.get_selected_pipeline_id()
        if not pipeline_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите трубопровод для редактирования")
            return

        pipeline = self.repo.get_by_id(pipeline_id)
        if not pipeline:
            QMessageBox.warning(self, "Предупреждение",
                              "Трубопровод не найден")
            return

        dialog = PipelineDialog(self.db, self, pipeline)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_pipeline = dialog.get_pipeline_data()
                self.repo.update(updated_pipeline)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Трубопровод успешно обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось обновить трубопровод: {str(e)}")

    def on_delete(self):
        """Обработчик удаления трубопровода"""
        pipeline_id = self.get_selected_pipeline_id()
        if not pipeline_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите трубопровод для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить трубопровод?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(pipeline_id)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Трубопровод успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось удалить трубопровод: {str(e)}")