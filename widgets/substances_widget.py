# widgets/substances_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QLineEdit,
                               QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.substance_repo import SubstanceRepository
from models.substance import Substance, SubstanceType
from .substance_dialog import SubstanceDialog


class SubstancesWidget(QWidget):
    """Виджет для отображения и управления списком веществ"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = SubstanceRepository(db)
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
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_input)

        # Фильтр по классу вещества
        filter_layout.addWidget(QLabel("Класс опасности:"))
        self.class_filter = QComboBox()
        self.class_filter.addItem("Все")
        self.class_filter.addItems(["1", "2", "3", "4"])
        self.class_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.class_filter)

        # Фильтр по типу вещества
        filter_layout.addWidget(QLabel("Тип вещества:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("Все")
        for sub_type in SubstanceType:
            self.type_filter.addItem(SubstanceType.get_display_name(sub_type))
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Наименование", "Класс", "Тип",
            "Плотность", "Температура вспышки",
            "Температура кипения", "Молекулярная масса"
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
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

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Получаем выбранные фильтры
        class_text = self.class_filter.currentText()
        type_text = self.type_filter.currentText()
        search_text = self.search_input.text().strip()

        # Получаем все вещества
        substances = self.repo.get_all()

        # Применяем фильтры
        if class_text != "Все":
            substances = [sub for sub in substances
                         if sub.class_substance == int(class_text)]

        if type_text != "Все":
            substances = [sub for sub in substances
                         if SubstanceType.get_display_name(sub.sub_type) == type_text]

        if search_text:
            substances = [sub for sub in substances
                         if search_text.lower() in sub.sub_name.lower()]

        # Заполняем таблицу
        self.table.setRowCount(len(substances))

        for i, substance in enumerate(substances):
            # ID
            item = QTableWidgetItem(str(substance.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Наименование
            item = QTableWidgetItem(substance.sub_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Класс
            item = QTableWidgetItem(str(substance.class_substance))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Тип
            item = QTableWidgetItem(SubstanceType.get_display_name(substance.sub_type))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Плотность
            density = "-" if substance.density_liquid is None else f"{substance.density_liquid:.2f}"
            item = QTableWidgetItem(density)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Температура вспышки
            flash_point = "-" if substance.flash_point is None else f"{substance.flash_point:.2f}"
            item = QTableWidgetItem(flash_point)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Температура кипения
            boiling_temp = "-" if substance.boiling_temperature_liquid is None else f"{substance.boiling_temperature_liquid:.2f}"
            item = QTableWidgetItem(boiling_temp)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

            # Молекулярная масса
            mol_weight = "-" if substance.molecular_weight is None else f"{substance.molecular_weight:.2f}"
            item = QTableWidgetItem(mol_weight)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_substance_id(self) -> int:
        """Получение ID выбранного вещества"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления вещества"""
        dialog = SubstanceDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                substance = dialog.get_substance_data()
                self.repo.create(substance)
                self.load_data()
                QMessageBox.information(self, "Информация", "Вещество успешно добавлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить вещество: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования вещества"""
        substance_id = self.get_selected_substance_id()
        if not substance_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите вещество для редактирования")
            return

        substance = self.repo.get_by_id(substance_id)
        if not substance:
            QMessageBox.warning(self, "Предупреждение", "Вещество не найдено")
            return

        dialog = SubstanceDialog(self, substance)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_substance = dialog.get_substance_data()
                self.repo.update(updated_substance)
                self.load_data()
                QMessageBox.information(self, "Информация", "Вещество успешно обновлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось обновить вещество: {str(e)}")

    def on_delete(self):
        """Обработчик удаления вещества"""
        substance_id = self.get_selected_substance_id()
        if not substance_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите вещество для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить вещество?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(substance_id)
                self.load_data()
                QMessageBox.information(self, "Информация", "Вещество успешно удалено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось удалить вещество: {str(e)}")