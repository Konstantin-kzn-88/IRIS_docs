# models/equipment.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EquipmentType(Enum):
    """Типы оборудования"""
    PIPELINE = "Pipeline"
    PUMP = "Pump"
    TECHNOLOGICAL_DEVICE = "Technological_device"
    TANK = "Tank"
    TRUCK_TANK = "Truck_tank"
    COMPRESSOR = "Compressor"

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
    coordinate: Optional[str]
    pressure: float
    temperature: float

@dataclass
class Pipeline(BaseEquipment):
    """Модель трубопровода"""
    diameter_category: str  # "Менее 75 мм", "От 75 до 150 мм", "Более 150 мм"
    length_meters: float
    diameter_pipeline: float
    flow: Optional[float]
    time_out: Optional[float]

@dataclass
class Pump(BaseEquipment):
    """Модель насоса"""
    pump_type: str  # "Центробежные герметичные", "Центробежные с уплотнениями", "Поршневые"
    volume: Optional[float]
    flow: Optional[float]
    time_out: Optional[float]
