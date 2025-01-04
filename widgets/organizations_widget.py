# widgets/organizations_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QLineEdit, QDialog)
from widgets.organization_dialog import OrganizationDialog
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.organization_repo import OrganizationRepository
from models.organization import Organization
from datetime import datetime


class OrganizationsWidget(QWidget):
    """Виджет для отображения и управления списком организаций"""

    def __init__(self, db: DatabaseConnection):
        super().__init__()
        self.db = db
        self.repo = OrganizationRepository(db)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем основной layout
        layout = QVBoxLayout(self)

        # Создаем поле поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Основные поля
        self.table.setHorizontalHeaderLabels([
            "ID", "Наименование", "Полное наименование",
            "Форма собственности", "Руководитель",
            "Телефон", "Email"
        ])

        # Растягиваем заголовки
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

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
        organizations = self.repo.get_all()

        self.table.setRowCount(len(organizations))

        for i, org in enumerate(organizations):
            # ID
            item = QTableWidgetItem(str(org.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            # Наименование
            item = QTableWidgetItem(org.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            # Полное наименование
            item = QTableWidgetItem(org.full_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            # Форма собственности
            item = QTableWidgetItem(org.org_form)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            # Руководитель
            head_name = org.head_name if org.head_name else '-'
            item = QTableWidgetItem(head_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            # Телефон
            phone = org.phone if org.phone else '-'
            item = QTableWidgetItem(phone)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            # Email
            email = org.email if org.email else '-'
            item = QTableWidgetItem(email)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

    def on_search(self, text: str):
        """Обработчик поиска по таблице"""
        if not text:
            self.load_data()
            return

        organizations = self.repo.search(text)

        self.table.setRowCount(len(organizations))

        for i, org in enumerate(organizations):
            # Заполняем строку так же, как в load_data
            item = QTableWidgetItem(str(org.id))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)

            item = QTableWidgetItem(org.name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)

            item = QTableWidgetItem(org.full_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item)

            item = QTableWidgetItem(org.org_form)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item)

            head_name = org.head_name if org.head_name else '-'
            item = QTableWidgetItem(head_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item)

            phone = org.phone if org.phone else '-'
            item = QTableWidgetItem(phone)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, item)

            email = org.email if org.email else '-'
            item = QTableWidgetItem(email)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, item)

    def get_selected_organization_id(self) -> int:
        """Получение ID выбранной организации"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        # Берем ID из первой колонки выбранной строки
        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text())

    def on_add(self):
        """Обработчик добавления организации"""
        dialog = OrganizationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                organization = dialog.get_organization_data()
                self.repo.create(organization)
                self.load_data()
                QMessageBox.information(self, "Информация", "Организация успешно добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить организацию: {str(e)}")

    def on_edit(self):
        """Обработчик редактирования организации"""
        org_id = self.get_selected_organization_id()
        if not org_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите организацию для редактирования")
            return

        # Получаем организацию из БД
        organization = self.repo.get_by_id(org_id)
        if not organization:
            QMessageBox.warning(self, "Предупреждение", "Организация не найдена")
            return

        # Открываем диалог редактирования
        dialog = OrganizationDialog(self, organization)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                updated_organization = dialog.get_organization_data()
                self.repo.update(updated_organization)
                self.load_data()
                QMessageBox.information(self, "Информация", "Организация успешно обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить организацию: {str(e)}")

    def on_delete(self):
        """Обработчик удаления организации"""
        org_id = self.get_selected_organization_id()
        if not org_id:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите организацию для удаления")
            return

        # Получаем количество связанных объектов
        dangerous_objects = self.db.execute_query(
            "SELECT COUNT(*) as count FROM dangerous_objects WHERE organization_id = ?",
            (org_id,)
        )
        opo_count = dangerous_objects[0]['count'] if dangerous_objects else 0

        # Формируем предупреждение
        warning_text = (
            "Вы действительно хотите удалить организацию?\n\n"
            f"Связанные объекты, которые также будут удалены:\n"
            f"- Опасных производственных объектов: {opo_count}\n"
            "- Все связанные проекты и расчеты\n\n"
            "Это действие невозможно отменить."
        )

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            warning_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удаляем связанные записи в правильном порядке
                with self.db.get_cursor() as cursor:
                    # Получаем список ОПО
                    cursor.execute(
                        "SELECT id FROM dangerous_objects WHERE organization_id = ?",
                        (org_id,)
                    )
                    opo_ids = [row['id'] for row in cursor.fetchall()]

                    # Удаляем записи из всех связанных таблиц
                    for opo_id in opo_ids:
                        cursor.execute(
                            "DELETE FROM calculation_results WHERE project_code IN "
                            "(SELECT project_code FROM projects WHERE opo_id = ?)",
                            (opo_id,)
                        )
                        cursor.execute(
                            "DELETE FROM projects WHERE opo_id = ?",
                            (opo_id,)
                        )

                    # Удаляем ОПО
                    cursor.execute(
                        "DELETE FROM dangerous_objects WHERE organization_id = ?",
                        (org_id,)
                    )

                    # Удаляем организацию
                    cursor.execute(
                        "DELETE FROM organizations WHERE id = ?",
                        (org_id,)
                    )

                self.load_data()
                QMessageBox.information(
                    self, "Информация",
                    "Организация и все связанные данные успешно удалены"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Не удалось удалить организацию: {str(e)}"
                )