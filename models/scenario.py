# models/scenario.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DepressurizationType(Enum):
    """Типы разгерметизации"""
    PARTIAL = "partial"
    FULL = "full"

class CalculationMethod(Enum):
    """Методы расчета последствий"""
    STRAIT_FIRE = "strait_fire"
    GAS_JET = "gas_jet"
    LIQUID_JET = "liquid_jet"
    FLASH = "flash"
    FIRE_BALL = "fire_ball"
    EXPLOSION = "explosion"
    TOXI = "toxi"
    TOXI_SPILL = "toxi_spill"
    NO_FACTORS = "no_factors"

@dataclass
class Scenario:
    """Доменная модель сценария"""
    id: Optional[int]
    equipment_id: int
    depressurization_type: DepressurizationType
    probability: float
    calculation_method: CalculationMethod
    tree_branch: int

    def __post_init__(self):
        """Валидация после инициализации"""
        if not 0 <= self.probability <= 1:
            raise ValueError("Вероятность должна быть от 0 до 1")