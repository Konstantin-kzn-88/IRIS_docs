# models/dangerous_object.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class HazardClass(Enum):
    """Классы опасности ОПО"""
    CLASS_I = "I"
    CLASS_II = "II"
    CLASS_III = "III"
    CLASS_IV = "IV"

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

