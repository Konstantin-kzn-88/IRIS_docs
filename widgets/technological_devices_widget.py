# widgets/technological_devices_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QLineEdit,
                             QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from models.equipment import TechnologicalDevice, EquipmentType
from .technological_device_dialog import TechnologicalDeviceDialog


class TechnologicalDevicesWidget(QWidget):
    """Виджет для отображения и управления списком технологических устройств"""

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

        # Фильтр по типу устройства
        filter_layout.addWidget(QLabel("Тип устройства:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("Все")
        self.type_filter.addItems([
            "Сосуды хранения под давлением",
            "Технологические аппараты",
            "Химические реакторы"
        ])
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Код проекта", "Название",
            "Проект", "Тип устройства",
            "Объем (м³)", "Степень заполнения",
            "Давление (МПа)", "Температура (°C)"
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
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)

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
        device_type = self.type_filter.currentText()
        search_text = self.search_input.text().strip()

        # Получаем все технологические устройства
        all_equipment = self.repo.get_by_type(EquipmentType.TECHNOLOGICAL_DEVICE)
        devices = [eq for eq in all_equipment if isinstance(eq, TechnologicalDevice)]

        # Применяем фильтры
        filtered_devices = []
        for device in devices:
            # Получаем проект
            project = self.project_repo.get_by_id(device.project_id)
            if not project:
                continue

            # Применяем фильтр по проекту
            if project_id and device.project_id != project_id:
                continue

            # Применяем фильтр по типу устройства
            if device_type != "Все" and device.device_type != device_type:
                continue

            # Применяем текстовый поиск
            if search_text:
                search_lower = search_text.lower()
                project_code = project.project_code or ""
                if not (search_lower in device.name.lower() or
                       search_lower in project_code.lower()):
                    continue

            filtered_devices.append((device, project))

        # Заполняем таблицу
        self.table.setRowCount(len(filtered_devices))

        for i, (device, project) in enumerate(filtered_devices):
            # ID
            item = QTableWidgetItem(str(device.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Код проекта
            item = QTableWidgetItem(project.project_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Название
            item = QTableWidgetItem(device.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Проект
            item = QTableWidgetItem(project.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Тип устройства
            item = QTableWidgetItem(device.device_type)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Объем
            volume = "-" if device.volume is None else f"{device.volume:.2f}"
            item = QTableWidgetItem(volume)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Степень заполнения
            filling = "-" if device.degree_filling is None else f"{device.degree_filling:.2%}"
            item = QTableWidgetItem(filling)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

            # Давление
            item = QTableWidgetItem(f"{device.pressure:.2f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

            # Температура
            item = QTableWidgetItem(f"{device.temperature:.1f}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 8, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_device_id(self) -> int:
        """Получение ID выбранного устройства"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления устройства"""
        dialog = TechnologicalDeviceDialog(self.db, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                device = dialog.get_device_data()
                self.repo.create(device)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Устройство успешно добавлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось добавить устройство: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования устройства"""
        device_id = self.get_selected_device_id()
        if not device_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите устройство для редактирования")
            return

        device = self.repo.get_by_id(device_id)
        if not device:
            QMessageBox.warning(self, "Предупреждение",
                              "Устройство не найдено")
            return

        dialog = TechnologicalDeviceDialog(self.db, self, device)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_device = dialog.get_device_data()
                self.repo.update(updated_device)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Устройство успешно обновлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось обновить устройство: {str(e)}")

    def on_delete(self):
        """Обработчик удаления устройства"""
        device_id = self.get_selected_device_id()
        if not device_id:
            QMessageBox.warning(self, "Предупреждение",
                              "Выберите устройство для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить устройство?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(device_id)
                self.load_data()
                QMessageBox.information(self, "Информация",
                                      "Устройство успешно удалено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                   f"Не удалось удалить устройство: {str(e)}")