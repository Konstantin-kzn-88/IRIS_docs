"""
substance.py — модель "Вещество" для Программы анализа промышленного риска.

Состав модуля:
- SubstanceType: перечисление категорий вещества (для выбора расчётных моделей).
- CompositionComponent / FractionBasis: описание состава (для смесей).
- PhysicalProperties: физические свойства.
- ExplosionHazard: пожаро- и взрывоопасность (расширено новыми параметрами).
- ToxicHazard: токсическая опасность.
- ProtectiveMeasures: меры безопасности и реагирования.
- Substance: верхнеуровневая сущность.
- main(): пример запуска модуля.

Единицы измерения фиксированы в полях классов.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict


# -----------------------------
# Классификация вещества
# -----------------------------
class SubstanceType(Enum):
    """
    Категория вещества для расчётных модулей промышленного риска.
    """
    FLAMMABLE_LIQUID = 0                 # ЛВЖ
    FLAMMABLE_LIQUID_TOXIC = 1           # ЛВЖ с токсичностью
    FLAMMABLE_GAS = 2                    # Горючий газ
    FLAMMABLE_GAS_TOXIC = 3              # Горючий газ с токсичностью
    LIQUEFIED_GAS = 4                    # Сжиженный газ
    LIQUEFIED_GAS_TOXIC = 5              # Сжиженный газ с токсичностью
    TOXIC_LIQUID_LOW_VOLATILITY = 6      # Токсичная жидкость низкой испаряемости
    TOXIC_GAS = 7                        # Токсичный газ
    TOXIC_LIQUEFIED_GAS = 8              # Токсичный сжиженный газ


class FractionBasis(Enum):
    """
    Основа долей состава смеси.
    """
    MASS = "mass"      # массовые доли
    MOLE = "mole"      # мольные доли
    VOLUME = "volume"  # объёмные доли


@dataclass(frozen=True)
class CompositionComponent:
    """
    Компонент состава смеси.
    fraction: доля компонента 0..1 (основание долей задаётся composition_basis).
    """
    name: str
    formula: Optional[str] = None
    fraction: float = 0.0


# -----------------------------
# Блоки свойств
# -----------------------------
@dataclass
class PhysicalProperties:
    """
    Физические свойства.

    Единицы:
      - molecular_mass: кг/моль
      - rho_liquid: кг/м3
      - rho_gas: кг/м3
      - heat_of_vaporization: Дж/кг
      - boiling_point_c: °C
    """
    molecular_mass: Optional[float] = None
    rho_liquid: Optional[float] = None
    rho_gas: Optional[float] = None
    heat_of_vaporization: Optional[float] = None
    boiling_point_c: Optional[float] = None

    def validate(self) -> List[str]:
        errors: List[str] = []
        for field_name in ("molecular_mass", "rho_liquid", "rho_gas", "heat_of_vaporization"):
            val = getattr(self, field_name)
            if val is not None and val <= 0:
                errors.append(f"{field_name} должен быть > 0 (получено {val}).")
        return errors


@dataclass
class ExplosionHazard:
    """
    Пожаро- и взрывоопасные свойства.

    Единицы:
      - flash_point_c: °C
      - lel_vol_percent: % об. (нижний концентрационный предел воспламеняемости/взрываемости)
      - autoignition_temp_c: °C

      - energy_reserve_factor: безразмерный коэффициент (1 или 2)
      - expansion_ratio: степень расширения продуктов сгорания (4 или 7)
      - heat_of_combustion_kj_kg: кДж/кг
      - specific_burning_rate: кг/(с·м²)
    """

    # Базовые показатели
    flash_point_c: Optional[float] = None
    lel_vol_percent: Optional[float] = None
    autoignition_temp_c: Optional[float] = None

    # Дополнения для расчётов взрыва/горения
    energy_reserve_factor: Optional[int] = None         # 1 или 2
    expansion_ratio: Optional[int] = None               # 4 или 7
    heat_of_combustion_kj_kg: Optional[float] = None    # кДж/кг
    specific_burning_rate: Optional[float] = None       # кг/(с·м²)

    def validate(self) -> List[str]:
        errors: List[str] = []

        if self.lel_vol_percent is not None and not (0 < self.lel_vol_percent < 100):
            errors.append(
                f"lel_vol_percent должен быть в диапазоне (0, 100) (получено {self.lel_vol_percent})."
            )

        if self.energy_reserve_factor is not None and self.energy_reserve_factor not in (1, 2):
            errors.append(
                "energy_reserve_factor должен принимать значение 1 или 2 "
                f"(получено {self.energy_reserve_factor})."
            )

        if self.expansion_ratio is not None and self.expansion_ratio not in (4, 7):
            errors.append(
                "expansion_ratio должен принимать значение 4 или 7 "
                f"(получено {self.expansion_ratio})."
            )

        if self.heat_of_combustion_kj_kg is not None and self.heat_of_combustion_kj_kg <= 0:
            errors.append(
                "heat_of_combustion_kj_kg должен быть > 0 "
                f"(получено {self.heat_of_combustion_kj_kg})."
            )

        if self.specific_burning_rate is not None and self.specific_burning_rate <= 0:
            errors.append(
                "specific_burning_rate должен быть > 0 "
                f"(получено {self.specific_burning_rate})."
            )

        return errors


@dataclass
class ToxicHazard:
    """
    Токсическая опасность.

    Единицы:
      - pdk_mg_m3: мг/м3
      - lethal_toxic_dose_mg_min_l: мг*мин/л
      - threshold_toxic_dose_mg_min_l: мг*мин/л
    """
    hazard_class: Optional[int] = None
    pdk_mg_m3: Optional[float] = None
    lethal_toxic_dose_mg_min_l: Optional[float] = None
    threshold_toxic_dose_mg_min_l: Optional[float] = None

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.hazard_class is not None and self.hazard_class <= 0:
            errors.append(f"hazard_class должен быть положительным (получено {self.hazard_class}).")

        for field_name in ("pdk_mg_m3", "lethal_toxic_dose_mg_min_l", "threshold_toxic_dose_mg_min_l"):
            val = getattr(self, field_name)
            if val is not None and val <= 0:
                errors.append(f"{field_name} должен быть > 0 (получено {val}).")
        return errors


@dataclass
class ProtectiveMeasures:
    """
    Меры безопасности, реагирования и первая помощь.
    """
    precautions: Optional[str] = None
    impact_on_people_and_environment: Optional[str] = None
    ppe_and_collective_protection: Optional[str] = None
    neutralization_methods: Optional[str] = None
    first_aid: Optional[str] = None


# -----------------------------
# Верхнеуровневая сущность
# -----------------------------
@dataclass
class Substance:
    """
    Базовый объект "Вещество" для анализа промышленного риска.
    """
    # Идентификация
    name: str
    substance_type: SubstanceType
    formula: Optional[str] = None

    # Состав (для смесей)
    composition_basis: FractionBasis = FractionBasis.MASS
    composition: List[CompositionComponent] = field(default_factory=list)

    # Свойства
    physical: PhysicalProperties = field(default_factory=PhysicalProperties)
    explosion: ExplosionHazard = field(default_factory=ExplosionHazard)
    toxic: ToxicHazard = field(default_factory=ToxicHazard)

    # Доп. характеристики
    reactivity: Optional[str] = None
    odor: Optional[str] = None
    corrosivity: Optional[str] = None

    # Меры
    measures: ProtectiveMeasures = field(default_factory=ProtectiveMeasures)

    # Метаданные
    notes: Optional[str] = None
    sources: Dict[str, str] = field(default_factory=dict)

    def validate(self, *, strict_composition_sum: bool = False, sum_tolerance: float = 1e-6) -> List[str]:
        """
        Валидация объекта.

        strict_composition_sum:
          - False: допускается неполный состав (сумма < 1.0), но сумма > 1.0 — ошибка.
          - True: сумма долей должна быть 1.0 ± tolerance.
        """
        errors: List[str] = []

        if not self.name or not self.name.strip():
            errors.append("name не должен быть пустым.")

        if self.composition:
            total = 0.0
            for i, c in enumerate(self.composition, start=1):
                if not c.name or not c.name.strip():
                    errors.append(f"composition[{i}].name не должен быть пустым.")
                if not (0.0 <= c.fraction <= 1.0):
                    errors.append(f"composition[{i}].fraction должен быть в диапазоне [0, 1] (получено {c.fraction}).")
                total += c.fraction

            if strict_composition_sum:
                if abs(total - 1.0) > sum_tolerance:
                    errors.append(f"Сумма долей состава должна быть 1.0 (получено {total}).")
            else:
                if total > 1.0 + sum_tolerance:
                    errors.append(f"Сумма долей состава превышает 1.0 (получено {total}).")

        errors.extend(self.physical.validate())
        errors.extend(self.explosion.validate())
        errors.extend(self.toxic.validate())

        return errors

    @property
    def is_mixture(self) -> bool:
        return len(self.composition) > 0

    def to_dict(self) -> dict:
        """
        Экспорт в словарь (под JSON/YAML).
        """
        return {
            "name": self.name,
            "substance_type": self.substance_type.name,
            "formula": self.formula,
            "composition_basis": self.composition_basis.value,
            "composition": [
                {"name": c.name, "formula": c.formula, "fraction": c.fraction}
                for c in self.composition
            ],
            "physical": self.physical.__dict__,
            "explosion": self.explosion.__dict__,
            "toxic": self.toxic.__dict__,
            "reactivity": self.reactivity,
            "odor": self.odor,
            "corrosivity": self.corrosivity,
            "measures": self.measures.__dict__,
            "notes": self.notes,
            "sources": self.sources,
        }


# -----------------------------
# main: пример запуска модуля
# -----------------------------
def main() -> None:
    """
    Пример использования модели.
    """
    acetone = Substance(
        name="Ацетон",
        substance_type=SubstanceType.FLAMMABLE_LIQUID,
        formula="C3H6O",
        notes="Пример для демонстрации структуры."
    )

    # Физические свойства (примерные значения)
    acetone.physical.molecular_mass = 0.05808   # кг/моль
    acetone.physical.rho_liquid = 790.0         # кг/м3
    acetone.physical.boiling_point_c = 56.0     # °C

    # Взрывоопасность / пожароопасность
    acetone.explosion.flash_point_c = -20.0
    acetone.explosion.lel_vol_percent = 2.6
    acetone.explosion.autoignition_temp_c = 465.0

    # Новые поля (по вашему запросу)
    acetone.explosion.energy_reserve_factor = 1          # 1 или 2
    acetone.explosion.expansion_ratio = 4                # 4 или 7
    acetone.explosion.heat_of_combustion_kj_kg = 29500.0 # кДж/кг (пример)
    acetone.explosion.specific_burning_rate = 0.03       # кг/(с·м²) (пример)

    # Токсичность (пример)
    acetone.toxic.hazard_class = 4
    acetone.toxic.pdk_mg_m3 = 200.0

    # Прочее
    acetone.odor = "Характерный, резкий"
    acetone.reactivity = "Сильные окислители; возможны реакции при нагреве/искрообразовании."
    acetone.corrosivity = "Низкая; совместимость с материалами уточнять по SDS."

    # Меры
    acetone.measures.precautions = "Исключить источники зажигания; обеспечить вентиляцию; избегать вдыхания паров."
    acetone.measures.first_aid = "При вдыхании — свежий воздух; при попадании на кожу — промыть водой; при ухудшении — врач."
    acetone.measures.ppe_and_collective_protection = (
        "Очки, перчатки, вентиляция; при высоких концентрациях — фильтрующий/изолирующий СИЗОД."
    )
    acetone.measures.neutralization_methods = (
        "Сбор сорбентом; утилизация по регламенту; предотвращать попадание в канализацию."
    )

    # Источники (пример трассируемости)
    acetone.sources = {
        "flash_point": "SDS производителя (пример)",
        "pdk": "Норматив/методика предприятия (пример)",
        "heat_of_combustion": "Справочник/методика (пример)",
    }

    # Проверка
    errors = acetone.validate()

    print("=== Substance Demo ===")
    print(f"Name: {acetone.name}")
    print(f"Type: {acetone.substance_type.name} (code={acetone.substance_type.value})")
    print(f"Formula: {acetone.formula}")
    print(f"Is mixture: {acetone.is_mixture}")
    print()

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f" - {e}")
    else:
        print("Validation: OK")

    print()
    print("Export to dict:")
    print(acetone.to_dict())


if __name__ == "__main__":
    main()
