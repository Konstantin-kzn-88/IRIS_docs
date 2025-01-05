# models/equipment.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class EquipmentType(Enum):
    """Типы оборудования"""
    PIPELINE = "Pipeline"
    PUMP = "Pump"
    TECHNOLOGICAL_DEVICE = "Technological_device"
    TANK = "Tank"
    TRUCK_TANK = "Truck_tank"
    COMPRESSOR = "Compressor"

    @classmethod
    def get_display_name(cls, value: 'EquipmentType') -> str:
        """Получение отображаемого имени типа оборудования"""
        names = {
            cls.PIPELINE: "Трубопровод",
            cls.PUMP: "Насос",
            cls.TECHNOLOGICAL_DEVICE: "Технологическое устройство",
            cls.TANK: "Резервуар",
            cls.TRUCK_TANK: "Автоцистерна",
            cls.COMPRESSOR: "Компрессор"
        }
        return names.get(value, str(value))


@dataclass
class BaseEquipment:
    """Базовая модель оборудования"""
    id: Optional[int]
    project_id: int
    substance_id: int
    name: str
    equipment_type: EquipmentType
    component_enterprise: Optional[str]
    sub_id: Optional[str]
    pressure: float
    temperature: float
    expected_casualties: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'substance_id': self.substance_id,
            'name': self.name,
            'equipment_type': self.equipment_type.value,
            'component_enterprise': self.component_enterprise,
            'sub_id': self.sub_id,
            'pressure': self.pressure,
            'temperature': self.temperature,
            'expected_casualties': self.expected_casualties
        }

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Наименование': self.name,
            'Тип оборудования': EquipmentType.get_display_name(self.equipment_type),
            'Компонент предприятия': self.component_enterprise or '-',
            'Идентификатор подсистемы': self.sub_id or '-',
            'Давление': f"{self.pressure:.2f}",
            'Температура': f"{self.temperature:.2f}",
            'Прогноз погибших': str(self.expected_casualties) if self.expected_casualties is not None else '-'
        }

    def validate(self) -> None:
        """Базовая валидация оборудования"""
        if not self.name:
            raise ValueError("Наименование оборудования не может быть пустым")

        if self.pressure < 0:
            raise ValueError("Давление не может быть отрицательным")

        if self.expected_casualties is not None and self.expected_casualties < 0:
            raise ValueError("Прогнозируемое количество погибших не может быть отрицательным")

        if self.project_id <= 0:
            raise ValueError("Некорректный ID проекта")

        if self.substance_id <= 0:
            raise ValueError("Некорректный ID вещества")


@dataclass
class Pipeline(BaseEquipment):
    """Модель трубопровода"""
    diameter_category: str  # "Менее 75 мм", "От 75 до 150 мм", "Более 150 мм"
    length_meters: float
    diameter_pipeline: float
    flow: Optional[float]
    time_out: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipeline':
        """Создание объекта из словаря"""
        base_data = {
            'id': data.get('id'),
            'project_id': data['project_id'],
            'substance_id': data['substance_id'],
            'name': data['name'],
            'equipment_type': EquipmentType(data['equipment_type']),
            'component_enterprise': data.get('component_enterprise'),
            'sub_id': data.get('sub_id'),
            'pressure': data['pressure'],
            'temperature': data['temperature'],
            'expected_casualties': data.get('expected_casualties')
        }

        pipeline_data = {
            'diameter_category': data['diameter_category'],
            'length_meters': data['length_meters'],
            'diameter_pipeline': data['diameter_pipeline'],
            'flow': data.get('flow'),
            'time_out': data.get('time_out')
        }

        return cls(**base_data, **pipeline_data)

@dataclass
class Pump(BaseEquipment):
    """Модель насоса"""
    pump_type: str  # "Центробежные герметичные", "Центробежные с уплотнениями", "Поршневые"
    volume: Optional[float]
    flow: Optional[float]
    time_out: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        base_dict = super().to_dict()
        pump_dict = {
            'pump_type': self.pump_type,
            'volume': self.volume,
            'flow': self.flow,
            'time_out': self.time_out
        }
        return {**base_dict, **pump_dict}

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        base_display = super().to_display_dict()
        pump_display = {
            'Тип насоса': self.pump_type,
            'Объем': f"{self.volume:.2f}" if self.volume is not None else "-",
            'Расход': f"{self.flow:.2f}" if self.flow is not None else "-",
            'Время выброса': f"{self.time_out:.2f}" if self.time_out is not None else "-"
        }
        return {**base_display, **pump_display}

    def validate(self) -> None:
        """Валидация насоса"""
        if self.pump_type not in ["Центробежные герметичные", "Центробежные с уплотнениями", "Поршневые"]:
            raise ValueError("Неверный тип насоса")
        if self.volume is not None and self.volume <= 0:
            raise ValueError("Объем должен быть положительным")
        if self.flow is not None and self.flow <= 0:
            raise ValueError("Расход должен быть положительным")
        if self.time_out is not None and self.time_out <= 0:
            raise ValueError("Время выброса должно быть положительным")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pump':
        """Создание объекта из словаря"""
        base_data = {
            'id': data.get('id'),
            'project_id': data['project_id'],
            'substance_id': data['substance_id'],
            'name': data['name'],
            'equipment_type': EquipmentType(data['equipment_type']),
            'component_enterprise': data.get('component_enterprise'),
            'sub_id': data.get('sub_id'),
            'pressure': data['pressure'],
            'temperature': data['temperature'],
            'expected_casualties': data.get('expected_casualties')
        }

        pump_data = {
            'pump_type': data.get('pump_type', 'Центробежные герметичные'),  # значение по умолчанию
            'volume': data.get('volume'),
            'flow': data.get('flow'),
            'time_out': data.get('time_out')
        }

        return cls(**base_data, **pump_data)

@dataclass
class TechnologicalDevice(BaseEquipment):
    """Модель технологического устройства"""
    device_type: str  # "Сосуды хранения под давлением", "Технологические аппараты", "Химические реакторы"
    volume: Optional[float]
    degree_filling: Optional[float]  # степень заполнения
    spill_square: Optional[float]    # площадь пролива

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        base_dict = super().to_dict()
        device_dict = {
            'device_type': self.device_type,
            'volume': self.volume,
            'degree_filling': self.degree_filling,
            'spill_square': self.spill_square
        }
        return {**base_dict, **device_dict}

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        base_display = super().to_display_dict()
        device_display = {
            'Тип устройства': self.device_type,
            'Объем': f"{self.volume:.2f}" if self.volume is not None else "-",
            'Степень заполнения': f"{self.degree_filling:.2f}" if self.degree_filling is not None else "-",
            'Площадь пролива': f"{self.spill_square:.2f}" if self.spill_square is not None else "-"
        }
        return {**base_display, **device_display}

    def validate(self) -> None:
        """Валидация технологического устройства"""
        valid_types = [
            "Сосуды хранения под давлением",
            "Технологические аппараты",
            "Химические реакторы"
        ]
        if self.device_type not in valid_types:
            raise ValueError("Неверный тип технологического устройства")
        if self.volume is not None and self.volume <= 0:
            raise ValueError("Объем должен быть положительным")
        if self.degree_filling is not None and not 0 <= self.degree_filling <= 1:
            raise ValueError("Степень заполнения должна быть от 0 до 1")
        if self.spill_square is not None and self.spill_square <= 0:
            raise ValueError("Площадь пролива должна быть положительной")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnologicalDevice':
        """Создание объекта из словаря"""
        base_data = {
            'id': data.get('id'),
            'project_id': data['project_id'],
            'substance_id': data['substance_id'],
            'name': data['name'],
            'equipment_type': EquipmentType(data['equipment_type']),
            'component_enterprise': data.get('component_enterprise'),
            'sub_id': data.get('sub_id'),
            'pressure': data['pressure'],
            'temperature': data['temperature'],
            'expected_casualties': data.get('expected_casualties')
        }

        device_data = {
            'device_type': data.get('device_type', 'Технологические аппараты'),  # значение по умолчанию
            'volume': data.get('volume'),
            'degree_filling': data.get('degree_filling'),
            'spill_square': data.get('spill_square')
        }

        return cls(**base_data, **device_data)

@dataclass
class Tank(BaseEquipment):
    """Модель стационарного резервуара"""
    tank_type: str  # "Одностенный", "С внешней защитной оболочкой", "С двойной оболочкой", "Полной герметизации"
    volume: Optional[float]
    degree_filling: Optional[float]
    spill_square: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        base_dict = super().to_dict()
        tank_dict = {
            'tank_type': self.tank_type,
            'volume': self.volume,
            'degree_filling': self.degree_filling,
            'spill_square': self.spill_square
        }
        return {**base_dict, **tank_dict}

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        base_display = super().to_display_dict()
        tank_display = {
            'Тип резервуара': self.tank_type,
            'Объем': f"{self.volume:.2f}" if self.volume is not None else "-",
            'Степень заполнения': f"{self.degree_filling:.2%}" if self.degree_filling is not None else "-",
            'Площадь пролива': f"{self.spill_square:.2f}" if self.spill_square is not None else "-"
        }
        return {**base_display, **tank_display}

    def validate(self) -> None:
        """Валидация резервуара"""
        super().validate()
        valid_types = [
            "Одностенный",
            "С внешней защитной оболочкой",
            "С двойной оболочкой",
            "Полной герметизации"
        ]
        if self.tank_type not in valid_types:
            raise ValueError("Неверный тип резервуара")
        if self.volume is not None and self.volume <= 0:
            raise ValueError("Объем должен быть положительным")
        if self.degree_filling is not None and not 0 <= self.degree_filling <= 1:
            raise ValueError("Степень заполнения должна быть от 0 до 1")
        if self.spill_square is not None and self.spill_square <= 0:
            raise ValueError("Площадь пролива должна быть положительной")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tank':
        """Создание объекта из словаря"""
        base_data = {
            'id': data.get('id'),
            'project_id': data['project_id'],
            'substance_id': data['substance_id'],
            'name': data['name'],
            'equipment_type': EquipmentType(data['equipment_type']),
            'component_enterprise': data.get('component_enterprise'),
            'sub_id': data.get('sub_id'),
            'pressure': data['pressure'],
            'temperature': data['temperature'],
            'expected_casualties': data.get('expected_casualties')
        }

        tank_data = {
            'tank_type': data.get('tank_type', 'Одностенный'),  # значение по умолчанию
            'volume': data.get('volume'),
            'degree_filling': data.get('degree_filling'),
            'spill_square': data.get('spill_square')
        }

        return cls(**base_data, **tank_data)

@dataclass
class TruckTank(BaseEquipment):
   """Модель автоцистерны"""
   pressure_type: str  # "Под избыточным давлением", "При атмосферном давлении"
   volume: Optional[float]
   degree_filling: Optional[float]
   spill_square: Optional[float]

   def to_dict(self) -> Dict[str, Any]:
       """Преобразование в словарь для БД"""
       base_dict = super().to_dict()
       truck_dict = {
           'pressure_type': self.pressure_type,
           'volume': self.volume,
           'degree_filling': self.degree_filling,
           'spill_square': self.spill_square
       }
       return {**base_dict, **truck_dict}

   def to_display_dict(self) -> Dict[str, str]:
       """Получение словаря для отображения в UI"""
       base_display = super().to_display_dict()
       truck_display = {
           'Тип давления': self.pressure_type,
           'Объем': f"{self.volume:.2f}" if self.volume is not None else "-",
           'Степень заполнения': f"{self.degree_filling:.2f}" if self.degree_filling is not None else "-",
           'Площадь пролива': f"{self.spill_square:.2f}" if self.spill_square is not None else "-"
       }
       return {**base_display, **truck_display}

   def validate(self) -> None:
       """Валидация автоцистерны"""
       valid_types = [
           "Под избыточным давлением",
           "При атмосферном давлении"
       ]
       if self.pressure_type not in valid_types:
           raise ValueError("Неверный тип давления")
       if self.volume is not None and self.volume <= 0:
           raise ValueError("Объем должен быть положительным")
       if self.degree_filling is not None and not 0 <= self.degree_filling <= 1:
           raise ValueError("Степень заполнения должна быть от 0 до 1")
       if self.spill_square is not None and self.spill_square <= 0:
           raise ValueError("Площадь пролива должна быть положительной")

   def __post_init__(self):
       """Валидация после инициализации"""
       self.validate()

   @classmethod
   def from_dict(cls, data: Dict[str, Any]) -> 'TruckTank':
       """Создание объекта из словаря"""
       base_data = {
           'id': data.get('id'),
           'project_id': data['project_id'],
           'substance_id': data['substance_id'],
           'name': data['name'],
           'equipment_type': EquipmentType(data['equipment_type']),
           'component_enterprise': data.get('component_enterprise'),
           'sub_id': data.get('sub_id'),
           'pressure': data['pressure'],
           'temperature': data['temperature'],
           'expected_casualties': data.get('expected_casualties')
       }

       truck_data = {
           'pressure_type': data.get('pressure_type', 'При атмосферном давлении'),  # значение по умолчанию
           'volume': data.get('volume'),
           'degree_filling': data.get('degree_filling'),
           'spill_square': data.get('spill_square')
       }

       return cls(**base_data, **truck_data)

@dataclass
class Compressor(BaseEquipment):
   """Модель компрессора"""
   comp_type: str
   volume: Optional[float]
   flow: Optional[float]
   time_out: Optional[float]

   def to_dict(self) -> Dict[str, Any]:
       """Преобразование в словарь для БД"""
       base_dict = super().to_dict()
       comp_dict = {
           'comp_type': self.comp_type,
           'volume': self.volume,
           'flow': self.flow,
           'time_out': self.time_out
       }
       return {**base_dict, **comp_dict}

   def to_display_dict(self) -> Dict[str, str]:
       """Получение словаря для отображения в UI"""
       base_display = super().to_display_dict()
       comp_display = {
           'Тип компрессора': self.comp_type,
           'Объем': f"{self.volume:.2f}" if self.volume is not None else "-",
           'Расход': f"{self.flow:.2f}" if self.flow is not None else "-",
           'Время выброса': f"{self.time_out:.2f}" if self.time_out is not None else "-"
       }
       return {**base_display, **comp_display}

   def validate(self) -> None:
       """Валидация компрессора"""
       if not self.comp_type:
           raise ValueError("Тип компрессора не может быть пустым")
       if self.volume is not None and self.volume <= 0:
           raise ValueError("Объем должен быть положительным")
       if self.flow is not None and self.flow <= 0:
           raise ValueError("Расход должен быть положительным")
       if self.time_out is not None and self.time_out <= 0:
           raise ValueError("Время выброса должно быть положительным")

   def __post_init__(self):
       """Валидация после инициализации"""
       self.validate()