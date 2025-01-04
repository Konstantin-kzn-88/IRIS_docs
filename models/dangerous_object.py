# models/dangerous_object.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class HazardClass(Enum):
    """Классы опасности ОПО"""
    CLASS_I = "I"
    CLASS_II = "II"
    CLASS_III = "III"
    CLASS_IV = "IV"

    @classmethod
    def get_display_name(cls, value: 'HazardClass') -> str:
        """Получение отображаемого имени класса опасности"""
        names = {
            cls.CLASS_I: "I класс",
            cls.CLASS_II: "II класс",
            cls.CLASS_III: "III класс",
            cls.CLASS_IV: "IV класс"
        }
        return names.get(value, str(value))


@dataclass
class DangerousObject:
    """Доменная модель опасного производственного объекта"""
    id: Optional[int]
    organization_id: int
    name: str
    reg_number: str
    hazard_class: HazardClass
    location: str
    employee_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для БД"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'reg_number': self.reg_number,
            'hazard_class': self.hazard_class.value,  # Сохраняем значение enum
            'location': self.location,
            'employee_count': self.employee_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DangerousObject':
        """Создание объекта из словаря"""
        return cls(
            id=data.get('id'),
            organization_id=data['organization_id'],
            name=data['name'],
            reg_number=data['reg_number'],
            hazard_class=HazardClass(data['hazard_class']),  # Преобразуем строку в enum
            location=data['location'],
            employee_count=data['employee_count']
        )

    def to_display_dict(self) -> Dict[str, str]:
        """Получение словаря для отображения в UI"""
        return {
            'Наименование': self.name,
            'Рег. номер': self.reg_number,
            'Класс опасности': HazardClass.get_display_name(self.hazard_class),
            'Местоположение': self.location,
            'Количество сотрудников': str(self.employee_count)
        }

    def validate(self) -> None:
        """Валидация объекта"""
        if self.employee_count <= 0:
            raise ValueError("Количество сотрудников должно быть положительным числом")

        if not self.reg_number:
            raise ValueError("Регистрационный номер не может быть пустым")

        # Проверка формата регистрационного номера (пример)
        # АХХ-ХХХХХ-ХХХХ
        import re
        reg_pattern = r'^[А-Я]\d{2}-\d{5}-\d{4}$'
        if not re.match(reg_pattern, self.reg_number):
            raise ValueError("Неверный формат регистрационного номера")

    def __post_init__(self):
        """Валидация после инициализации"""
        self.validate()