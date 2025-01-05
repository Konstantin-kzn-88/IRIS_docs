# widgets/compressors_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QLineEdit,
                             QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from models.equipment import Compressor, EquipmentType
from .compressor_dialog import CompressorDialog


class CompressorsWidget(QWidget):
    """Виджет для отображения и управления списком компрессоров"""

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

        # Фильтр по типу компрессора
        filter_layout.addWidget(QLabel("Тип компрессора:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("Все")
        self.type_filter.addItems([
            "Поршневой компрессор",
            "Центробежный компрессор",
            "Винтовой компрессор"
        ])
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Код проекта", "Название",
            "Проект", "Тип компрессора",
            "Объем (м³)", "Расход (кг/с)", "Давление (МПа)"
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
        comp_type = self.type_filter.currentText()
        search_text = self.search_input.text().strip()

        # Получаем все компрессоры
        all_equipment = self.repo.get_by_type(EquipmentType.COMPRESSOR)
        compressors = [eq for eq in all_equipment if isinstance(eq, Compressor)]

        # Применяем фильтры
        filtered_compressors = []
        for compressor in compressors:
            # Получаем проект
            project = self.project_repo.get_by_id(compressor.project_id)
            if not project:
                continue

            # Применяем фильтр по проекту
            if project_id and compressor.project_id != project_id:
                continue

            # Применяем фильтр по типу компрессора
            if comp_type != "Все" and compressor.comp_type != comp_type:
                continue

            # Применяем текстовый поиск
            if search_text:
                search_lower = search_text.lower()
                project_code = project.project_code or ""
                if not (search_lower in compressor.name.lower() or
                       search_lower in project_code.lower()):
                    continue

            filtered_compressors.append((compressor, project))

        # Заполняем таблицу
        self.table.setRowCount(len(filtered_compressors))

        for i, (compressor, project) in enumerate(filtered_compressors):
            # ID
            item = QTableWidgetItem(str(compressor.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Код проекта
            item = QTableWidgetItem(project.project_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Название
            item = QTableWidgetItem(compressor.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Проект
            item = QTableWidgetItem(project.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Тип компрессора
            item = QTableWidgetItem(compressor.comp_type)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Объем
            volume = "-" if compressor.volume is None else f"{compressor.volume:.2f}"
            item = QTableWidgetItem(volume)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Расход
            flow = "-" if compressor.flow is None else f"{compressor.flow:.2f}"
            item = QTableWidgetItem(flow)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

            # Давление
            item = QTableWidgetItem(f"{compressor.pressure:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_compressor_id(self) -> int:
        """Получение ID выбранного компрессора"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления компрессора"""
        dialog = CompressorDialog(self.db, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                compressor = dialog.get_compressor_data()
                self.repo.create(compressor)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Компрессор успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось добавить компрессор: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования компрессора"""
        compressor_id = self.get_selected_compressor_id()
        if not compressor_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите компрессор для редактирования")
            return

        compressor = self.repo.get_by_id(compressor_id)
        if not compressor:
            QMessageBox.warning(self, "Предупреждение",
                              "Компрессор не найден")
            return

        dialog = CompressorDialog(self.db, self, compressor)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_compressor = dialog.get_compressor_data()
                self.repo.update(updated_compressor)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Компрессор успешно обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось обновить компрессор: {str(e)}")

    def on_delete(self):
        """Обработчик удаления компрессора"""
        compressor_id = self.get_selected_compressor_id()
        if not compressor_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите компрессор для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить компрессор?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(compressor_id)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Компрессор успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось удалить компрессор: {str(e)}")