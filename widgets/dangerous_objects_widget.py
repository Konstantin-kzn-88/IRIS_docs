# widgets/dangerous_objects_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QLineEdit,
                               QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.dangerous_object_repo import DangerousObjectRepository
from database.repositories.organization_repo import OrganizationRepository
from models.dangerous_object import DangerousObject, HazardClass
from .dangerous_object_dialog import DangerousObjectDialog


class DangerousObjectsWidget(QWidget):
    """Виджет для отображения и управления списком ОПО"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = DangerousObjectRepository(db)
        self.org_repo = OrganizationRepository(db)
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
        self.search_input.setPlaceholderText("Поиск по названию или рег. номеру...")
        self.search_input.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_input)

        # Фильтр по классу опасности
        filter_layout.addWidget(QLabel("Класс опасности:"))
        self.hazard_class_filter = QComboBox()
        self.hazard_class_filter.addItem("Все")
        self.hazard_class_filter.addItems([
            HazardClass.get_display_name(HazardClass.CLASS_I),
            HazardClass.get_display_name(HazardClass.CLASS_II),
            HazardClass.get_display_name(HazardClass.CLASS_III),
            HazardClass.get_display_name(HazardClass.CLASS_IV)
        ])
        self.hazard_class_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.hazard_class_filter)

        # Фильтр по организации
        filter_layout.addWidget(QLabel("Организация:"))
        self.org_filter = QComboBox()
        self.org_filter.addItem("Все")
        self.load_organizations()
        self.org_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.org_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Организация", "Наименование",
            "Рег. номер", "Класс опасности", "Количество сотрудников"
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

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

    def load_organizations(self):
        """Загрузка списка организаций в фильтр"""
        organizations = self.org_repo.get_all()
        for org in organizations:
            self.org_filter.addItem(org.name, userData=org.id)

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Получаем выбранные фильтры
        hazard_class_text = self.hazard_class_filter.currentText()
        org_id = self.org_filter.currentData()
        search_text = self.search_input.text().strip()

        # Получаем все объекты
        objects = self.repo.get_all()

        # Применяем фильтры
        if hazard_class_text != "Все":
            objects = [obj for obj in objects
                       if HazardClass.get_display_name(obj.hazard_class) == hazard_class_text]

        if org_id:
            objects = [obj for obj in objects if obj.organization_id == org_id]

        if search_text:
            objects = [obj for obj in objects
                       if search_text.lower() in obj.name.lower() or
                       search_text.lower() in obj.reg_number.lower()]

        # Заполняем таблицу
        self.table.setRowCount(len(objects))

        for i, obj in enumerate(objects):
            # ID
            item = QTableWidgetItem(str(obj.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Организация
            org = self.org_repo.get_by_id(obj.organization_id)
            item = QTableWidgetItem(org.name if org else "Не найдена")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Наименование
            item = QTableWidgetItem(obj.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Рег. номер
            item = QTableWidgetItem(obj.reg_number)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Класс опасности
            item = QTableWidgetItem(HazardClass.get_display_name(obj.hazard_class))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Количество сотрудников
            item = QTableWidgetItem(str(obj.employee_count))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_object_id(self) -> int:
        """Получение ID выбранного ОПО"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления ОПО"""
        dialog = DangerousObjectDialog(self.db, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                obj = dialog.get_object_data()
                self.repo.create(obj)
                self.load_data()
                QMessageBox.information(self, "Информация", "ОПО успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить ОПО: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования ОПО"""
        obj_id = self.get_selected_object_id()
        if not obj_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите ОПО для редактирования")
            return

        obj = self.repo.get_by_id(obj_id)
        if not obj:
            QMessageBox.warning(self, "Предупреждение", "ОПО не найден")
            return

        dialog = DangerousObjectDialog(self.db, self, obj)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_obj = dialog.get_object_data()
                self.repo.update(updated_obj)
                self.load_data()
                QMessageBox.information(self, "Информация", "ОПО успешно обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось обновить ОПО: {str(e)}")

    def on_delete(self):
        """Обработчик удаления ОПО"""
        obj_id = self.get_selected_object_id()
        if not obj_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите ОПО для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить ОПО?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(obj_id)
                self.load_data()
                QMessageBox.information(self, "Информация", "ОПО успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось удалить ОПО: {str(e)}")