# models/substance.py
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

class SubstanceType(IntEnum):
    """Типы веществ"""
    LVJ = 0  # ЛВЖ
    LVJ_TOXIC = 1  # ЛВЖ токсичная
    SUG = 2  # СУГ
    SUG_TOXIC = 3  # СУГ токсичный
    GJ = 4  # ГЖ
    GG = 5  # ГГ
    GG_TOXIC = 6  # ГГ токсичный
    HOV = 7  # ХОВ

@dataclass
class Substance:
    """Доменная модель вещества"""
    id: Optional[int]
    sub_name: str
    class_substance: int  # 1-4
    sub_type: SubstanceType
    density_liquid: Optional[float]
    molecular_weight: Optional[float]
    boiling_temperature_liquid: Optional[float]
    heat_evaporation_liquid: Optional[float]
    adiabatic: Optional[float]
    heat_capacity_liquid: Optional[float]
    heat_of_combustion: Optional[float]
    sigma: Optional[int]  # 4 или 7
    energy_level: Optional[int]  # 1 или 2
    flash_point: Optional[float]
    auto_ignition_temp: Optional[float]
    lower_concentration_limit: Optional[float]
    upper_concentration_limit: Optional[float]
    threshold_toxic_dose: Optional[float]
    lethal_toxic_dose: Optional[float]

    def __post_init__(self):
        """Валидация после инициализации"""
        if not 1 <= self.class_substance <= 4:
            raise ValueError("class_substance должен быть от 1 до 4")
        if self.sigma is not None and self.sigma not in (4, 7):
            raise ValueError("sigma должна быть 4 или 7")
        if self.energy_level is not None and self.energy_level not in (1, 2):
            raise ValueError("energy_level должен быть 1 или 2")

