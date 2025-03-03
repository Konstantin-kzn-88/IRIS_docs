# excel_importer.py
import pandas as pd
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                               QComboBox, QFileDialog, QMessageBox, QGridLayout,
                               QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from database.db_connection import DatabaseConnection
from database.repositories.project_repo import ProjectRepository
from database.repositories.substance_repo import SubstanceRepository
from database.repositories.equipment_repo import EquipmentRepository
from models.equipment import Pipeline, Pump, TechnologicalDevice, Tank, TruckTank, Compressor, EquipmentType
from utilities.equipment_name_validator import validate_equipment_name


class ExcelImporter(QDialog):
    """Диалог импорта данных из Excel"""

    def __init__(self, db: DatabaseConnection, parent=None):
        super().__init__(parent)
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.substance_repo = SubstanceRepository(db)
        self.equipment_repo = EquipmentRepository(db)
        self.file_path = None
        self.df = None
        self.equipment_type = None
        self.setup_ui()
        self.setWindowTitle("Импорт данных из Excel")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout(self)

        # Выбор типа оборудования
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Трубопроводы",
            "Насосы",
            "Технологические устройства",
            "Резервуары",
            "Автоцистерны",
            "Компрессоры"
        ])
        layout.addWidget(QLabel("Выберите тип оборудования:"))
        layout.addWidget(self.type_combo)

        # Выбор проекта
        self.project_combo = QComboBox()
        self.load_projects()
        layout.addWidget(QLabel("Выберите проект:"))
        layout.addWidget(self.project_combo)

        # Кнопки выбора файла и загрузки шаблона
        button_layout = QGridLayout()

        self.select_file_btn = QPushButton("Выбрать файл Excel")
        self.select_file_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_btn, 0, 0)

        self.download_template_btn = QPushButton("Скачать шаблон")
        self.download_template_btn.clicked.connect(self.download_template)
        button_layout.addWidget(self.download_template_btn, 0, 1)

        layout.addLayout(button_layout)

        # Путь к файлу
        self.file_path_label = QLabel("Файл не выбран")
        layout.addWidget(self.file_path_label)

        # Таблица для предпросмотра
        layout.addWidget(QLabel("Предпросмотр данных:"))
        self.preview_table = QTableWidget()
        layout.addWidget(self.preview_table)

        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Кнопки действия
        button_layout = QGridLayout()

        self.import_btn = QPushButton("Импортировать")
        self.import_btn.clicked.connect(self.import_data)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn, 0, 0)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn, 0, 1)

        layout.addLayout(button_layout)

    def load_projects(self):
        """Загрузка списка проектов"""
        projects = self.project_repo.get_all()
        self.project_combo.clear()

        # Сортируем проекты сначала по коду проекта, затем по названию
        projects.sort(key=lambda x: (x.project_code or '', x.name))

        for project in projects:
            display_text = f"{project.project_code or '---'} | {project.name}"
            self.project_combo.addItem(display_text, userData=project.id)

    def select_file(self):
        """Выбор Excel файла"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Выбрать файл Excel", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(f"Выбран файл: {os.path.basename(file_path)}")
            self.load_preview()
            self.import_btn.setEnabled(True)

    def download_template(self):
        """Скачать шаблон Excel для выбранного типа оборудования"""
        equipment_type = self.type_combo.currentText()

        # Создаем шаблон в зависимости от типа оборудования
        if equipment_type == "Трубопроводы":
            df = pd.DataFrame({
                'Наименование': ['Наименование трубопровода (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['PIPE-001'],
                'Категория_диаметра': ['Менее 75 мм', 'От 75 до 150 мм', 'Более 150 мм'],
                'Длина_м': [100.0],
                'Диаметр_мм': [50.0],
                'Давление_МПа': [1.0],
                'Температура_C': [25.0],
                'Расход_кгс': [10.0],
                'Время_выброса_с': [60.0],
                'Доля_аварийного_участка': [1.0],
                'Ожидаемые_пострадавшие': [0]
            })
        elif equipment_type == "Насосы":
            df = pd.DataFrame({
                'Наименование': ['Наименование насоса (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['PUMP-001'],
                'Тип_насоса': ['Центробежные герметичные', 'Центробежные с уплотнениями', 'Поршневые'],
                'Объем_м3': [0.5],
                'Давление_МПа': [1.0],
                'Температура_C': [25.0],
                'Расход_кгс': [10.0],
                'Время_выброса_с': [60.0],
                'Ожидаемые_пострадавшие': [0]
            })
        elif equipment_type == "Технологические устройства":
            df = pd.DataFrame({
                'Наименование': ['Наименование устройства (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['TD-001'],
                'Тип_устройства': ['Сосуды хранения под давлением', 'Технологические аппараты', 'Химические реакторы'],
                'Объем_м3': [10.0],
                'Давление_МПа': [1.0],
                'Температура_C': [25.0],
                'Степень_заполнения': [0.8],
                'Площадь_пролива_м2': [50.0],
                'Ожидаемые_пострадавшие': [0]
            })
        elif equipment_type == "Резервуары":
            df = pd.DataFrame({
                'Наименование': ['Наименование резервуара (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['TANK-001'],
                'Тип_резервуара': ['Одностенный', 'С внешней защитной оболочкой', 'С двойной оболочкой',
                                   'Полной герметизации'],
                'Объем_м3': [100.0],
                'Давление_МПа': [0.2],
                'Температура_C': [25.0],
                'Степень_заполнения': [0.85],
                'Площадь_пролива_м2': [200.0],
                'Ожидаемые_пострадавшие': [0]
            })
        elif equipment_type == "Автоцистерны":
            df = pd.DataFrame({
                'Наименование': ['Наименование автоцистерны (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['TT-001'],
                'Тип_давления': ['Под избыточным давлением', 'При атмосферном давлении'],
                'Объем_м3': [30.0],
                'Давление_МПа': [0.2],
                'Температура_C': [25.0],
                'Степень_заполнения': [0.85],
                'Площадь_пролива_м2': [100.0],
                'Ожидаемые_пострадавшие': [0]
            })
        elif equipment_type == "Компрессоры":
            df = pd.DataFrame({
                'Наименование': ['Наименование компрессора (Компонент)'],
                'Проект_код': ['Код проекта (если известен)'],
                'Вещество': ['Название вещества'],
                'Компонент_предприятия': ['Цех №1'],
                'Идентификатор_подсистемы': ['COMP-001'],
                'Тип_компрессора': ['Поршневой компрессор', 'Центробежный компрессор', 'Винтовой компрессор'],
                'Объем_м3': [3.0],
                'Давление_МПа': [3.0],
                'Температура_C': [35.0],
                'Расход_кгс': [15.0],
                'Время_выброса_с': [120.0],
                'Ожидаемые_пострадавшие': [0]
            })

        # Диалог для сохранения шаблона
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(
            self, "Сохранить шаблон", f"Шаблон_{equipment_type}.xlsx", "Excel Files (*.xlsx)"
        )

        if save_path:
            df.to_excel(save_path, index=False)
            QMessageBox.information(
                self, "Успешно", f"Шаблон для {equipment_type} сохранен в:\n{save_path}"
            )

    def load_preview(self):
        """Загрузка данных из Excel для предпросмотра"""
        try:
            self.df = pd.read_excel(self.file_path)
            self.update_preview_table()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить файл Excel:\n{str(e)}"
            )
            self.df = None
            self.import_btn.setEnabled(False)

    def update_preview_table(self):
        """Обновление таблицы предпросмотра"""
        if self.df is None:
            return

        # Настройка таблицы
        self.preview_table.setRowCount(min(10, len(self.df)))
        self.preview_table.setColumnCount(len(self.df.columns))
        self.preview_table.setHorizontalHeaderLabels(self.df.columns)

        # Заполнение данными
        for i in range(min(10, len(self.df))):
            for j, col in enumerate(self.df.columns):
                value = str(self.df.iloc[i, j])
                item = QTableWidgetItem(value)
                self.preview_table.setItem(i, j, item)

        # Автоматическая настройка ширины столбцов
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def import_data(self):
        """Импорт данных из Excel в базу данных"""
        if self.df is None or self.file_path is None:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите файл Excel для импорта"
            )
            return

        # Получаем тип оборудования
        equipment_type_text = self.type_combo.currentText()

        # Получаем ID проекта
        project_id = self.project_combo.currentData()
        if not project_id:
            QMessageBox.warning(
                self, "Предупреждение", "Выберите проект для импорта"
            )
            return

        # Преобразуем тип оборудования в enum
        equipment_type_map = {
            "Трубопроводы": EquipmentType.PIPELINE,
            "Насосы": EquipmentType.PUMP,
            "Технологические устройства": EquipmentType.TECHNOLOGICAL_DEVICE,
            "Резервуары": EquipmentType.TANK,
            "Автоцистерны": EquipmentType.TRUCK_TANK,
            "Компрессоры": EquipmentType.COMPRESSOR
        }

        self.equipment_type = equipment_type_map.get(equipment_type_text)
        if not self.equipment_type:
            QMessageBox.warning(
                self, "Предупреждение", "Неизвестный тип оборудования"
            )
            return

        # Показываем прогресс-бар
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.df))
        self.progress_bar.setValue(0)

        # Импортируем данные
        success_count = 0
        error_count = 0
        error_messages = []

        for i, row in self.df.iterrows():
            try:
                # Обновляем прогресс
                self.progress_bar.setValue(i + 1)

                # Проверяем наименование
                name = str(row.get('Наименование', ''))
                if not name or name == 'nan':
                    error_count += 1
                    error_messages.append(f"Строка {i + 1}: Отсутствует наименование")
                    continue

                # Проверяем формат наименования
                is_valid, error_message = validate_equipment_name(name)
                if not is_valid:
                    error_count += 1
                    error_messages.append(f"Строка {i + 1}: {error_message}")
                    continue

                # Получаем вещество
                substance_name = str(row.get('Вещество', ''))
                if not substance_name or substance_name == 'nan':
                    error_count += 1
                    error_messages.append(f"Строка {i + 1}: Отсутствует вещество")
                    continue

                # Ищем вещество в базе данных
                substances = self.substance_repo.get_all()
                substance = next((s for s in substances if s.sub_name.lower() == substance_name.lower()), None)

                if not substance:
                    error_count += 1
                    error_messages.append(f"Строка {i + 1}: Вещество '{substance_name}' не найдено в базе данных")
                    continue

                # Создаем оборудование в зависимости от типа
                equipment = None

                try:
                    if self.equipment_type == EquipmentType.PIPELINE:
                        equipment = self._create_pipeline(row, project_id, substance.id)
                    elif self.equipment_type == EquipmentType.PUMP:
                        equipment = self._create_pump(row, project_id, substance.id)
                    elif self.equipment_type == EquipmentType.TECHNOLOGICAL_DEVICE:
                        equipment = self._create_tech_device(row, project_id, substance.id)
                    elif self.equipment_type == EquipmentType.TANK:
                        equipment = self._create_tank(row, project_id, substance.id)
                    elif self.equipment_type == EquipmentType.TRUCK_TANK:
                        equipment = self._create_truck_tank(row, project_id, substance.id)
                    elif self.equipment_type == EquipmentType.COMPRESSOR:
                        equipment = self._create_compressor(row, project_id, substance.id)
                except KeyError as e:
                    error_count += 1
                    error_messages.append(f"Строка {i + 1}: Отсутствует обязательное поле: {str(e)}")
                    continue

                # Сохраняем оборудование в базу данных
                if equipment:
                    self.equipment_repo.create(equipment)
                    success_count += 1

            except Exception as e:
                error_count += 1
                error_messages.append(f"Строка {i + 1}: {str(e)}")

        # Показываем результат
        if error_count > 0:
            error_text = "\n".join(error_messages[:10])
            if len(error_messages) > 10:
                error_text += f"\n... и еще {len(error_messages) - 10} ошибок"

            result_message = (
                f"Импорт завершен с ошибками.\n"
                f"Успешно импортировано: {success_count}\n"
                f"Ошибок: {error_count}\n\n"
                f"Детали ошибок:\n{error_text}"
            )

            QMessageBox.warning(self, "Результат импорта", result_message)
        else:
            QMessageBox.information(
                self, "Успешно", f"Импорт завершен успешно. Импортировано записей: {success_count}"
            )

        self.accept()

    def _safe_float(self, value, default=0.0):
        """Безопасное преобразование в float"""
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _create_pipeline(self, row, project_id, substance_id):
        """Создание объекта трубопровода из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Категория диаметра
        diameter_category = str(row.get('Категория_диаметра', 'Менее 75 мм'))
        if diameter_category not in ["Менее 75 мм", "От 75 до 150 мм", "Более 150 мм"]:
            diameter_category = "Менее 75 мм"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return Pipeline(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.PIPELINE,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 1.0), 1.0),
            temperature=self._safe_float(row.get('Температура_C', 25.0), 25.0),
            expected_casualties=expected_casualties,
            diameter_category=diameter_category,
            length_meters=self._safe_float(row.get('Длина_м', 100.0), 100.0),
            diameter_pipeline=self._safe_float(row.get('Диаметр_мм', 50.0), 50.0),
            flow=self._safe_float(row.get('Расход_кгс', None)),
            time_out=self._safe_float(row.get('Время_выброса_с', None)),
            accident_rate=self._safe_float(row.get('Доля_аварийного_участка', 1.0), 1.0)
        )

    def _create_pump(self, row, project_id, substance_id):
        """Создание объекта насоса из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Тип насоса
        pump_type = str(row.get('Тип_насоса', 'Центробежные герметичные'))
        if pump_type not in ["Центробежные герметичные", "Центробежные с уплотнениями", "Поршневые"]:
            pump_type = "Центробежные герметичные"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return Pump(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.PUMP,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 1.0), 1.0),
            temperature=self._safe_float(row.get('Температура_C', 25.0), 25.0),
            expected_casualties=expected_casualties,
            pump_type=pump_type,
            volume=self._safe_float(row.get('Объем_м3', None)),
            flow=self._safe_float(row.get('Расход_кгс', None)),
            time_out=self._safe_float(row.get('Время_выброса_с', None))
        )

    def _create_tech_device(self, row, project_id, substance_id):
        """Создание объекта технологического устройства из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Тип устройства
        device_type = str(row.get('Тип_устройства', 'Технологические аппараты'))
        if device_type not in ["Сосуды хранения под давлением", "Технологические аппараты", "Химические реакторы"]:
            device_type = "Технологические аппараты"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return TechnologicalDevice(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.TECHNOLOGICAL_DEVICE,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 1.0), 1.0),
            temperature=self._safe_float(row.get('Температура_C', 25.0), 25.0),
            expected_casualties=expected_casualties,
            device_type=device_type,
            volume=self._safe_float(row.get('Объем_м3', None)),
            degree_filling=self._safe_float(row.get('Степень_заполнения', None)),
            spill_square=self._safe_float(row.get('Площадь_пролива_м2', None))
        )

    def _create_tank(self, row, project_id, substance_id):
        """Создание объекта резервуара из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Тип резервуара
        tank_type = str(row.get('Тип_резервуара', 'Одностенный'))
        if tank_type not in ["Одностенный", "С внешней защитной оболочкой", "С двойной оболочкой",
                             "Полной герметизации"]:
            tank_type = "Одностенный"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return Tank(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.TANK,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 0.2), 0.2),
            temperature=self._safe_float(row.get('Температура_C', 25.0), 25.0),
            expected_casualties=expected_casualties,
            tank_type=tank_type,
            volume=self._safe_float(row.get('Объем_м3', None)),
            degree_filling=self._safe_float(row.get('Степень_заполнения', None)),
            spill_square=self._safe_float(row.get('Площадь_пролива_м2', None))
        )

    def _create_truck_tank(self, row, project_id, substance_id):
        """Создание объекта автоцистерны из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Тип давления
        pressure_type = str(row.get('Тип_давления', 'Под избыточным давлением'))
        if pressure_type not in ["Под избыточным давлением", "При атмосферном давлении"]:
            pressure_type = "Под избыточным давлением"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return TruckTank(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.TRUCK_TANK,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 0.2), 0.2),
            temperature=self._safe_float(row.get('Температура_C', 25.0), 25.0),
            expected_casualties=expected_casualties,
            pressure_type=pressure_type,
            volume=self._safe_float(row.get('Объем_м3', None)),
            degree_filling=self._safe_float(row.get('Степень_заполнения', None)),
            spill_square=self._safe_float(row.get('Площадь_пролива_м2', None))
        )

    def _create_compressor(self, row, project_id, substance_id):
        """Создание объекта компрессора из данных Excel"""
        name = str(row['Наименование'])

        # Получаем компонент предприятия
        component = str(row.get('Компонент_предприятия', ''))
        if not component or component == 'nan':
            # Если не указан, попробуем извлечь из наименования
            import re
            match = re.search(r'\((.*?)\)', name)
            if match:
                component = match.group(1)

        # Идентификатор подсистемы
        sub_id = str(row.get('Идентификатор_подсистемы', ''))
        if sub_id == 'nan':
            sub_id = None

        # Тип компрессора
        comp_type = str(row.get('Тип_компрессора', 'Центробежный компрессор'))
        if comp_type not in ["Поршневой компрессор", "Центробежный компрессор", "Винтовой компрессор"]:
            comp_type = "Центробежный компрессор"

        # Ожидаемые пострадавшие
        expected_casualties = 0
        try:
            casualties_value = row.get('Ожидаемые_пострадавшие', 0)
            if not pd.isna(casualties_value):
                expected_casualties = int(casualties_value)
        except (ValueError, TypeError):
            pass

        return Compressor(
            id=None,
            project_id=project_id,
            substance_id=substance_id,
            name=name,
            equipment_type=EquipmentType.COMPRESSOR,
            component_enterprise=component if component else None,
            sub_id=sub_id,
            pressure=self._safe_float(row.get('Давление_МПа', 3.0), 3.0),
            temperature=self._safe_float(row.get('Температура_C', 35.0), 35.0),
            expected_casualties=expected_casualties,
            comp_type=comp_type,
            volume=self._safe_float(row.get('Объем_м3', None)),
            flow=self._safe_float(row.get('Расход_кгс', None)),
            time_out=self._safe_float(row.get('Время_выброса_с', None))
        )