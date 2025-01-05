# database/repositories/equipment_repo.py
from typing import List, Optional, Dict, Any, Type
from models.equipment import (
    BaseEquipment, Pipeline, Pump, TechnologicalDevice,
    Tank, TruckTank, Compressor, EquipmentType
)
from ..db_connection import DatabaseConnection


class EquipmentRepository:
    """Репозиторий для работы с оборудованием"""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def _get_equipment_class(self, equipment_type: EquipmentType) -> Type[BaseEquipment]:
        """Получение класса по типу оборудования"""
        type_to_class = {
            EquipmentType.PIPELINE: Pipeline,
            EquipmentType.PUMP: Pump,
            EquipmentType.TECHNOLOGICAL_DEVICE: TechnologicalDevice,
            EquipmentType.TANK: Tank,
            EquipmentType.TRUCK_TANK: TruckTank,
            EquipmentType.COMPRESSOR: Compressor
        }
        return type_to_class[equipment_type]

    def _create_specific_equipment(self, base_id: int, equipment: BaseEquipment) -> None:
        """Создание специфичных данных оборудования"""
        if isinstance(equipment, Pipeline):
            query = """
                INSERT INTO pipelines (
                    id, diameter_category, length_meters,
                    diameter_pipeline, flow, time_out
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.diameter_category,
                equipment.length_meters, equipment.diameter_pipeline,
                equipment.flow, equipment.time_out
            )
        elif isinstance(equipment, Pump):
            query = """
                INSERT INTO pumps (
                    id, pump_type, volume, flow, time_out
                ) VALUES (?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.pump_type, equipment.volume,
                equipment.flow, equipment.time_out
            )
        elif isinstance(equipment, TechnologicalDevice):
            query = """
                INSERT INTO technological_devices (
                    id, device_type, volume,
                    degree_filling, spill_square
                ) VALUES (?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.device_type, equipment.volume,
                equipment.degree_filling, equipment.spill_square
            )
        elif isinstance(equipment, Tank):
            query = """
                INSERT INTO tanks (
                    id, tank_type, volume,
                    degree_filling, spill_square
                ) VALUES (?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.tank_type, equipment.volume,
                equipment.degree_filling, equipment.spill_square
            )
        elif isinstance(equipment, TruckTank):
            query = """
                INSERT INTO truck_tanks (
                    id, pressure_type, volume,
                    degree_filling, spill_square
                ) VALUES (?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.pressure_type, equipment.volume,
                equipment.degree_filling, equipment.spill_square
            )
        elif isinstance(equipment, Compressor):
            query = """
                INSERT INTO compressors (
                    id, comp_type, volume, flow, time_out
                ) VALUES (?, ?, ?, ?, ?)
            """
            params = (
                base_id, equipment.comp_type, equipment.volume,
                equipment.flow, equipment.time_out
            )

        self.db.execute_query(query, params)

    def create(self, equipment: BaseEquipment) -> BaseEquipment:
        """Создание нового оборудования"""
        # Сначала создаем базовую запись
        base_query = """
            INSERT INTO base_equipment (
                project_id, substance_id, name,
                equipment_type, component_enterprise,
                sub_id, pressure, temperature,
                expected_casualties
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        base_params = (
            equipment.project_id,
            equipment.substance_id,
            equipment.name,
            equipment.equipment_type.value,
            equipment.component_enterprise,
            equipment.sub_id,
            equipment.pressure,
            equipment.temperature,
            equipment.expected_casualties
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(base_query, base_params)
            base_id = cursor.lastrowid
            equipment.id = base_id

            # Затем создаем специфичные данные
            self._create_specific_equipment(base_id, equipment)

        return equipment

    def _load_specific_data(self, base_equipment: Dict[str, Any]) -> Dict[str, Any]:
        """Загрузка специфичных данных оборудования"""
        equipment_type = EquipmentType(base_equipment['equipment_type'])
        equipment_id = base_equipment['id']

        type_to_table = {
            EquipmentType.PIPELINE: 'pipelines',
            EquipmentType.PUMP: 'pumps',
            EquipmentType.TECHNOLOGICAL_DEVICE: 'technological_devices',
            EquipmentType.TANK: 'tanks',
            EquipmentType.TRUCK_TANK: 'truck_tanks',
            EquipmentType.COMPRESSOR: 'compressors'
        }

        table_name = type_to_table[equipment_type]

        # Добавляем проверку на пустой результат
        result = self.db.execute_query(f"SELECT * FROM {table_name} WHERE id = ?", (equipment_id,))
        if not result:
            # Если данные не найдены, возвращаем базовые данные с пустыми специфичными полями
            if equipment_type == EquipmentType.PUMP:
                return {
                    **base_equipment,
                    'pump_type': 'Центробежные герметичные',  # значение по умолчанию
                    'volume': None,
                    'flow': None,
                    'time_out': None
                }
            return base_equipment

        specific_data = dict(result[0])
        return {**base_equipment, **specific_data}

    def _get_equipment_from_row(self, row: Dict[str, Any]) -> BaseEquipment:
        """Создание объекта оборудования из строки БД"""
        equipment_type = EquipmentType(row['equipment_type'])
        equipment_class = self._get_equipment_class(equipment_type)

        # Загружаем специфичные данные
        full_data = self._load_specific_data(row)
        return equipment_class.from_dict(full_data)

    def get_by_id(self, equipment_id: int) -> Optional[BaseEquipment]:
        """Получение оборудования по id"""
        query = "SELECT * FROM base_equipment WHERE id = ?"
        result = self.db.execute_query(query, (equipment_id,))

        if result:
            return self._get_equipment_from_row(dict(result[0]))
        return None

    def get_by_project(self, project_id: int) -> List[BaseEquipment]:
        """Получение всего оборудования проекта"""
        query = """
            SELECT * FROM base_equipment 
            WHERE project_id = ?
            ORDER BY name
        """
        result = self.db.execute_query(query, (project_id,))
        return [self._get_equipment_from_row(dict(row)) for row in result]

    def get_by_type(self, equipment_type: EquipmentType) -> List[BaseEquipment]:
        """Получение оборудования определенного типа"""
        query = """
            SELECT * FROM base_equipment 
            WHERE equipment_type = ?
            ORDER BY name
        """
        result = self.db.execute_query(query, (equipment_type.value,))
        return [self._get_equipment_from_row(dict(row)) for row in result]

    def delete(self, equipment_id: int) -> bool:
        """Удаление оборудования"""
        # Каскадное удаление обеспечивается внешними ключами
        query = "DELETE FROM base_equipment WHERE id = ?"
        self.db.execute_query(query, (equipment_id,))
        return True

    def update(self, equipment: BaseEquipment) -> BaseEquipment:
        """Обновление оборудования"""
        # Обновляем базовые данные
        base_query = """
            UPDATE base_equipment SET
                project_id = ?,
                substance_id = ?,
                name = ?,
                equipment_type = ?,
                component_enterprise = ?,
                sub_id = ?,
                pressure = ?,
                temperature = ?,
                expected_casualties = ?
            WHERE id = ?
        """
        base_params = (
            equipment.project_id,
            equipment.substance_id,
            equipment.name,
            equipment.equipment_type.value,
            equipment.component_enterprise,
            equipment.sub_id,
            equipment.pressure,
            equipment.temperature,
            equipment.expected_casualties,
            equipment.id
        )

        with self.db.get_cursor() as cursor:
            cursor.execute(base_query, base_params)

            # Удаляем старые специфичные данные
            type_to_table = {
                EquipmentType.PIPELINE: 'pipelines',
                EquipmentType.PUMP: 'pumps',
                EquipmentType.TECHNOLOGICAL_DEVICE: 'technological_devices',
                EquipmentType.TANK: 'tanks',
                EquipmentType.TRUCK_TANK: 'truck_tanks',
                EquipmentType.COMPRESSOR: 'compressors'
            }

            table_name = type_to_table[equipment.equipment_type]
            delete_query = f"DELETE FROM {table_name} WHERE id = ?"
            cursor.execute(delete_query, (equipment.id,))

            # Создаем новые специфичные данные
            self._create_specific_equipment(equipment.id, equipment)

        return equipment


# Пример использования:
if __name__ == "__main__":
    db = DatabaseConnection("industrial_safety.db")
    repo = EquipmentRepository(db)

    try:
        # Создаем тестовый трубопровод
        pipeline = Pipeline(
            id=None,
            project_id=1,  # ID существующего проекта
            substance_id=1,  # ID существующего вещества
            name="Тестовый трубопровод",
            equipment_type=EquipmentType.PIPELINE,
            component_enterprise="Цех №1",
            sub_id="PIPE-001",
            pressure=1.5,
            temperature=25.0,
            expected_casualties=0,
            diameter_category="От 75 до 150 мм",
            length_meters=100.0,
            diameter_pipeline=100.0,
            flow=10.0,
            time_out=30.0
        )

        # Сохраняем в БД
        created_pipeline = repo.create(pipeline)
        print(f"Создан трубопровод с id: {created_pipeline.id}")

        # Получаем все трубопроводы
        all_pipelines = repo.get_by_type(EquipmentType.PIPELINE)
        print(f"Всего трубопроводов: {len(all_pipelines)}")

    finally:
        db.close()