# models/substance.py
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Dict, Any


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

    @classmethod
    def get_display_name(cls, value: 'SubstanceType') -> str:
        """Получение отображаемого имени типа вещества"""
        names = {
            cls.LVJ: "ЛВЖ",
            cls.LVJ_TOXIC: "ЛВЖ токсичная",
            cls.SUG: "СУГ",
            cls.SUG_TOXIC: "СУГ токсичный",
            cls.GJ: "ГЖ",
            cls.GG: "ГГ",
            cls.GG_TOXIC: "ГГ токсичный",
            cls.HOV: "ХОВ"
        }
        return names.get(value, str(value))


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

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'sub_name': self.sub_name,
            'class_substance': self.class_substance,
            'sub_type': int(self.sub_type),
            'density_liquid': self.density_liquid,
            'molecular_weight': self.molecular_weight,
            'boiling_temperature_liquid': self.boiling_temperature_liquid,
            'heat_evaporation_liquid': self.heat_evaporation_liquid,
            'adiabatic': self.adiabatic,
            'heat_capacity_liquid': self.heat_capacity_liquid,
            'heat_of_combustion': self.heat_of_combustion,
            'sigma': self.sigma,
            'energy_level': self.energy_level,
            'flash_point': self.flash_point,
            'auto_ignition_temp': self.auto_ignition_temp,
            'lower_concentration_limit': self.lower_concentration_limit,
            'upper_concentration_limit': self.upper_concentration_limit,
            'threshold_toxic_dose': self.threshold_toxic_dose,
            'lethal_toxic_dose': self.lethal_toxic_dose
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Substance':
        """Создание объекта из словаря"""
        return cls(
            id=data.get('id'),
            sub_name=data['sub_name'],
            class_substance=data['class_substance'],
            sub_type=SubstanceType(data['sub_type']),
            density_liquid=data.get('density_liquid'),
            molecular_weight=data.get('molecular_weight'),
            boiling_temperature_liquid=data.get('boiling_temperature_liquid'),
            heat_evaporation_liquid=data.get('heat_evaporation_liquid'),
            adiabatic=data.get('adiabatic'),
            heat_capacity_liquid=data.get('heat_capacity_liquid'),
            heat_of_combustion=data.get('heat_of_combustion'),
            sigma=data.get('sigma'),
            energy_level=data.get('energy_level'),
            flash_point=data.get('flash_point'),
            auto_ignition_temp=data.get('auto_ignition_temp'),
            lower_concentration_limit=data.get('lower_concentration_limit'),
            upper_concentration_limit=data.get('upper_concentration_limit'),
            threshold_toxic_dose=data.get('threshold_toxic_dose'),
            lethal_toxic_dose=data.get('lethal_toxic_dose')
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Наименование': self.sub_name,
            'Класс опасности': str(self.class_substance),
            'Тип вещества': SubstanceType.get_display_name(self.sub_type),
            'Плотность жидкости': f"{self.density_liquid:.2f}" if self.density_liquid is not None else "-",
            'Молекулярная масса': f"{self.molecular_weight:.2f}" if self.molecular_weight is not None else "-",
            'Температура кипения': f"{self.boiling_temperature_liquid:.2f}" if self.boiling_temperature_liquid is not None else "-",
            'Теплота испарения': f"{self.heat_evaporation_liquid:.2f}" if self.heat_evaporation_liquid is not None else "-",
            'Показатель адиабаты': f"{self.adiabatic:.2f}" if self.adiabatic is not None else "-",
            'Теплоемкость': f"{self.heat_capacity_liquid:.2f}" if self.heat_capacity_liquid is not None else "-",
            'Теплота сгорания': f"{self.heat_of_combustion:.2f}" if self.heat_of_combustion is not None else "-",
            'Сигма': str(self.sigma) if self.sigma is not None else "-",
            'Энергетический уровень': str(self.energy_level) if self.energy_level is not None else "-",
            'Температура вспышки': f"{self.flash_point:.2f}" if self.flash_point is not None else "-",
            'Температура самовоспламенения': f"{self.auto_ignition_temp:.2f}" if self.auto_ignition_temp is not None else "-",
            'Нижний концентрационный предел': f"{self.lower_concentration_limit:.2f}" if self.lower_concentration_limit is not None else "-",
            'Верхний концентрационный предел': f"{self.upper_concentration_limit:.2f}" if self.upper_concentration_limit is not None else "-",
            'Пороговая токсодоза': f"{self.threshold_toxic_dose:.2f}" if self.threshold_toxic_dose is not None else "-",
            'Смертельная токсодоза': f"{self.lethal_toxic_dose:.2f}" if self.lethal_toxic_dose is not None else "-"
        }

    def validate(self) -> None:
        """Валидация объекта"""
        if not self.sub_name:
            raise ValueError("Наименование вещества не может быть пустым")

        if not 1 <= self.class_substance <= 4:
            raise ValueError("class_substance должен быть от 1 до 4")

        if self.sigma is not None and self.sigma not in (4, 7):
            raise ValueError("sigma должна быть 4 или 7")

        if self.energy_level is not None and self.energy_level not in (1, 2):
            raise ValueError("energy_level должен быть 1 или 2")

        if self.lower_concentration_limit is not None and self.upper_concentration_limit is not None:
            if self.lower_concentration_limit > self.upper_concentration_limit:
                raise ValueError("Нижний концентрационный предел не может быть больше верхнего")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()