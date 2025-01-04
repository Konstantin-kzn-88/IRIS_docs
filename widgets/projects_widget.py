# widgets/projects_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QLineEdit,
                               QComboBox, QLabel)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from database.repositories.dangerous_object_repo import DangerousObjectRepository
from database.repositories.organization_repo import OrganizationRepository
from models.project import Project
from .project_dialog import ProjectDialog


class ProjectsWidget(QWidget):
    """Виджет для отображения и управления списком проектов"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = ProjectRepository(db)
        self.opo_repo = DangerousObjectRepository(db)
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
        self.search_input.setPlaceholderText("Поиск по названию или шифрам...")
        self.search_input.textChanged.connect(self.on_search)
        filter_layout.addWidget(self.search_input)

        # Фильтр по организации
        filter_layout.addWidget(QLabel("Организация:"))
        self.org_filter = QComboBox()
        self.org_filter.addItem("Все")
        self.load_organizations()
        self.org_filter.currentIndexChanged.connect(self.on_org_filter_changed)
        filter_layout.addWidget(self.org_filter)

        # Фильтр по ОПО
        filter_layout.addWidget(QLabel("ОПО:"))
        self.opo_filter = QComboBox()
        self.opo_filter.addItem("Все")
        self.load_dangerous_objects()
        self.opo_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.opo_filter)

        layout.addLayout(filter_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Организация", "ОПО", "Наименование",
            "Шифр проекта", "Шифр ДПБ",
            "Шифр РПЗ", "Шифр ГОЧС", "Шифр МПБ"
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
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

    def load_organizations(self):
        """Загрузка списка организаций в фильтр"""
        organizations = self.org_repo.get_all()
        for org in organizations:
            self.org_filter.addItem(org.name, userData=org.id)

    def load_dangerous_objects(self, org_id=None):
        """Загрузка списка ОПО в фильтр"""
        self.opo_filter.clear()
        self.opo_filter.addItem("Все")

        if org_id:
            dangerous_objects = self.opo_repo.get_by_organization(org_id)
        else:
            dangerous_objects = self.opo_repo.get_all()

        for obj in dangerous_objects:
            self.opo_filter.addItem(obj.name, userData=obj.id)

    def on_org_filter_changed(self, index):
        """Обработчик изменения фильтра организации"""
        # Обновляем список ОПО при смене организации
        org_id = self.org_filter.currentData()
        self.load_dangerous_objects(org_id)
        self.load_data()

    def load_data(self):
        """Загрузка данных в таблицу"""
        # Получаем выбранные фильтры
        org_id = self.org_filter.currentData()
        opo_id = self.opo_filter.currentData()
        search_text = self.search_input.text().strip()

        # Получаем все проекты
        projects = self.repo.get_all()

        # Применяем фильтры
        filtered_projects = []
        for proj in projects:
            # Получаем ОПО и организацию
            opo = self.opo_repo.get_by_id(proj.opo_id)
            if not opo:
                continue

            org = self.org_repo.get_by_id(opo.organization_id)
            if not org:
                continue

            # Применяем фильтр по организации
            if org_id and org.id != org_id:
                continue

            # Применяем фильтр по ОПО
            if opo_id and opo.id != opo_id:
                continue

            # Применяем текстовый поиск
            if search_text:
                search_lower = search_text.lower()
                if not (search_lower in proj.name.lower() or
                        (proj.project_code and search_lower in proj.project_code.lower()) or
                        (proj.dpb_code and search_lower in proj.dpb_code.lower()) or
                        (proj.rpz_code and search_lower in proj.rpz_code.lower()) or
                        (proj.gochs_code and search_lower in proj.gochs_code.lower()) or
                        (proj.mpb_code and search_lower in proj.mpb_code.lower())):
                    continue

            filtered_projects.append((proj, opo, org))

        # Заполняем таблицу
        self.table.setRowCount(len(filtered_projects))

        for i, (proj, opo, org) in enumerate(filtered_projects):
            # ID
            item = QTableWidgetItem(str(proj.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Организация
            item = QTableWidgetItem(org.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # ОПО
            item = QTableWidgetItem(opo.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Наименование
            item = QTableWidgetItem(proj.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Шифр проекта
            item = QTableWidgetItem(proj.project_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Шифр ДПБ
            item = QTableWidgetItem(proj.dpb_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Шифр РПЗ
            item = QTableWidgetItem(proj.rpz_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

            # Шифр ГОЧС
            item = QTableWidgetItem(proj.gochs_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, item)

            # Шифр МПБ
            item = QTableWidgetItem(proj.mpb_code or "-")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 8, item)

    def on_search(self, text: str):
        """Обработчик поиска"""
        self.load_data()

    def on_filter_changed(self, index: int):
        """Обработчик изменения фильтров"""
        self.load_data()

    def get_selected_project_id(self) -> int:
        """Получение ID выбранного проекта"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления проекта"""
        dialog = ProjectDialog(self.db, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                project = dialog.get_project_data()
                self.repo.create(project)
                self.load_data()
                QMessageBox.information(self, "Информация", "Проект успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить проект: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования проекта"""
        project_id = self.get_selected_project_id()
        if not project_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите проект для редактирования")
            return

        project = self.repo.get_by_id(project_id)
        if not project:
            QMessageBox.warning(self, "Предупреждение", "Проект не найден")
            return

        dialog = ProjectDialog(self.db, self, project)
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                updated_project = dialog.get_project_data()
                self.repo.update(updated_project)
                self.load_data()
                QMessageBox.information(self, "Информация", "Проект успешно обновлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось обновить проект: {str(e)}")

    def on_delete(self):
        """Обработчик удаления проекта"""
        project_id = self.get_selected_project_id()
        if not project_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите проект для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы действительно хотите удалить проект?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(project_id)
                self.load_data()
                QMessageBox.information(self, "Информация", "Проект успешно удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось удалить проект: {str(e)}")