# file: equipment_entities.py

from __future__ import annotations

from typing import Any, Dict, Optional


class EquipmentBase:
    """
    Базовый класс оборудования.
    Содержит общие параметры сценария пролива/испарения + давление + фазовое состояние
    + привязку к веществу + координаты (опционально).
    """

    # Допустимые значения фазового состояния (строго по вашему формату)
    ALLOWED_PHASE_STATES = ("ж.ф.", "г.ф.", "ж.ф.+г.ф.")
    # 0-линейный, 1-стационарный, 2-точечный
    ALLOWED_COORD_TYPES = (0, 1, 2)

    def __init__(
        self,
        substance_id: int,
        coords: Optional[Dict[str, Any]],
        coord_type: int,

        pressure_mpa: float,
        phase_state: str,

        spill_coefficient: float,
        spill_area_m2: float,
        substance_temperature_c: float,
        shutdown_time_s: float,
        evaporation_time_s: float,
    ):
        # Связь с веществом (обязательна)
        self.substance_id = int(substance_id)

        # Координаты могут быть None (вариант без графической части)
        self.coords = coords
        self.coord_type = int(coord_type)

        # Общие расчетные параметры
        self.pressure_mpa = float(pressure_mpa)
        self.phase_state = str(phase_state).strip()

        self.spill_coefficient = float(spill_coefficient)
        self.spill_area_m2 = float(spill_area_m2)
        self.substance_temperature_c = float(substance_temperature_c)
        self.shutdown_time_s = float(shutdown_time_s)
        self.evaporation_time_s = self._limit_evaporation_time(evaporation_time_s)

        # Валидация общих параметров
        self._validate_common_parameters()

    def _limit_evaporation_time(self, evaporation_time_s: float) -> float:
        """
        Фиксированное ограничение: если испарение > 3600 с, то принимаем 3600 с.
        """
        t = float(evaporation_time_s)
        return 3600.0 if t > 3600.0 else t

    def _validate_common_parameters(self) -> None:
        # Вещество обязательно
        if self.substance_id <= 0:
            raise ValueError("substance_id должен быть положительным (оборудование без вещества не допускается)")

        # Координатный тип обязателен и должен быть из списка
        if self.coord_type not in self.ALLOWED_COORD_TYPES:
            raise ValueError("coord_type должен быть 0 (линейный), 1 (стационарный) или 2 (точечный)")

        # Координаты могут быть None или dict
        if self.coords is not None and not isinstance(self.coords, dict):
            raise ValueError("coords должен быть None или dict (для JSON-хранения)")

        # Давление не может быть отрицательным
        if self.pressure_mpa < 0:
            raise ValueError("pressure_mpa (давление) не может быть отрицательным")

        # Фазовое состояние проверяем по допустимому списку
        if self.phase_state not in self.ALLOWED_PHASE_STATES:
            raise ValueError('phase_state должен быть одним из: "ж.ф.", "г.ф.", "ж.ф.+г.ф."')

        # Прочие ограничения
        if self.spill_coefficient < 0:
            raise ValueError("spill_coefficient не может быть отрицательным")

        if self.spill_area_m2 <= 0:
            raise ValueError("spill_area_m2 должна быть > 0")

        if self.shutdown_time_s < 0:
            raise ValueError("shutdown_time_s не может быть отрицательным")

        if self.evaporation_time_s <= 0:
            raise ValueError("evaporation_time_s должна быть > 0")

    def _common_dict(self) -> Dict[str, Any]:
        return {
            "substance_id": self.substance_id,
            "coords": self.coords,
            "coord_type": self.coord_type,

            "pressure_mpa": self.pressure_mpa,
            "phase_state": self.phase_state,

            "spill_coefficient": self.spill_coefficient,
            "spill_area_m2": self.spill_area_m2,
            "substance_temperature_c": self.substance_temperature_c,
            "shutdown_time_s": self.shutdown_time_s,
            "evaporation_time_s": self.evaporation_time_s,
        }


class TechPipeline(EquipmentBase):
    """
    Технологический трубопровод.

    Геометрия:
      - length_m: длина, м
      - diameter_mm: диаметр, мм
      - wall_thickness_mm: толщина стенки, мм

    Параметры частот (можно оставить None):
      - base_frequency_rupture_per_year: базовая частота разрыва/разгерметизации
      - base_frequency_depressurization_per_year: базовая частота декомпрессии
    """

    def __init__(
        self,
        length_m: float,
        diameter_mm: float,
        wall_thickness_mm: float,

        substance_id: int,
        coords: Optional[Dict[str, Any]],
        coord_type: int,

        pressure_mpa: float,
        phase_state: str,

        spill_coefficient: float,
        spill_area_m2: float,
        substance_temperature_c: float,
        shutdown_time_s: float,
        evaporation_time_s: float,

        base_frequency_rupture_per_year: Optional[float] = None,
        base_frequency_depressurization_per_year: Optional[float] = None,
    ):
        super().__init__(
            substance_id=substance_id,
            coords=coords,
            coord_type=coord_type,

            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s,
        )

        self.length_m = float(length_m)
        self.diameter_mm = float(diameter_mm)
        self.wall_thickness_mm = float(wall_thickness_mm)

        self.base_frequency_rupture_per_year = (
            None if base_frequency_rupture_per_year is None else float(base_frequency_rupture_per_year)
        )
        self.base_frequency_depressurization_per_year = (
            None if base_frequency_depressurization_per_year is None else float(base_frequency_depressurization_per_year)
        )

        self._validate_geometry()

    def _validate_geometry(self) -> None:
        if self.length_m <= 0:
            raise ValueError("length_m должна быть > 0")
        if self.diameter_mm <= 0:
            raise ValueError("diameter_mm должен быть > 0")
        if self.wall_thickness_mm <= 0:
            raise ValueError("wall_thickness_mm должна быть > 0")
        if self.wall_thickness_mm >= self.diameter_mm:
            raise ValueError("wall_thickness_mm должна быть меньше diameter_mm")

    def to_dict(self) -> Dict[str, Any]:
        d = self._common_dict()
        d.update(
            {
                "equipment_class": "TechPipeline",
                "length_m": self.length_m,
                "diameter_mm": self.diameter_mm,
                "wall_thickness_mm": self.wall_thickness_mm,
                "base_frequency_rupture_per_year": self.base_frequency_rupture_per_year,
                "base_frequency_depressurization_per_year": self.base_frequency_depressurization_per_year,
            }
        )
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TechPipeline":
        return TechPipeline(
            length_m=data.get("length_m", 0),
            diameter_mm=data.get("diameter_mm", 0),
            wall_thickness_mm=data.get("wall_thickness_mm", 0),

            substance_id=data.get("substance_id"),
            coords=data.get("coords"),
            coord_type=data.get("coord_type", 0),

            pressure_mpa=data.get("pressure_mpa", 0),
            phase_state=data.get("phase_state", "ж.ф."),

            spill_coefficient=data.get("spill_coefficient", 1),
            spill_area_m2=data.get("spill_area_m2", 1),
            substance_temperature_c=data.get("substance_temperature_c", 20),
            shutdown_time_s=data.get("shutdown_time_s", 0),
            evaporation_time_s=data.get("evaporation_time_s", 1),

            base_frequency_rupture_per_year=data.get("base_frequency_rupture_per_year"),
            base_frequency_depressurization_per_year=data.get("base_frequency_depressurization_per_year"),
        )


class PumpCompressorEquipment(EquipmentBase):
    """
    Насосно-компрессорное оборудование.

    equipment_type:
      0 - насос
      1 - компрессор
      2 - насос+компрессор

    Геометрия:
      - pipeline_diameter_mm: диаметр трубопровода, мм

    Частоты (можно None):
      - base_frequency_catastrophic_per_year
      - base_frequency_leak_per_year
    """

    ALLOWED_EQUIPMENT_TYPES = (0, 1, 2)

    def __init__(
        self,
        equipment_type: int,
        pipeline_diameter_mm: float,

        substance_id: int,
        coords: Optional[Dict[str, Any]],
        coord_type: int,

        pressure_mpa: float,
        phase_state: str,

        spill_coefficient: float,
        spill_area_m2: float,
        substance_temperature_c: float,
        shutdown_time_s: float,
        evaporation_time_s: float,

        base_frequency_catastrophic_per_year: Optional[float] = None,
        base_frequency_leak_per_year: Optional[float] = None,
    ):
        super().__init__(
            substance_id=substance_id,
            coords=coords,
            coord_type=coord_type,

            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s,
        )

        self.equipment_type = int(equipment_type)
        self.pipeline_diameter_mm = float(pipeline_diameter_mm)

        self.base_frequency_catastrophic_per_year = (
            None if base_frequency_catastrophic_per_year is None else float(base_frequency_catastrophic_per_year)
        )
        self.base_frequency_leak_per_year = (
            None if base_frequency_leak_per_year is None else float(base_frequency_leak_per_year)
        )

        self._validate_specific()

    def _validate_specific(self) -> None:
        if self.equipment_type not in self.ALLOWED_EQUIPMENT_TYPES:
            raise ValueError("equipment_type должен быть 0 (насос), 1 (компрессор) или 2 (насос+компрессор)")
        if self.pipeline_diameter_mm <= 0:
            raise ValueError("pipeline_diameter_mm должен быть > 0")

    def to_dict(self) -> Dict[str, Any]:
        d = self._common_dict()
        d.update(
            {
                "equipment_class": "PumpCompressorEquipment",
                "equipment_type": self.equipment_type,
                "pipeline_diameter_mm": self.pipeline_diameter_mm,
                "base_frequency_catastrophic_per_year": self.base_frequency_catastrophic_per_year,
                "base_frequency_leak_per_year": self.base_frequency_leak_per_year,
            }
        )
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PumpCompressorEquipment":
        return PumpCompressorEquipment(
            equipment_type=data.get("equipment_type", 0),
            pipeline_diameter_mm=data.get("pipeline_diameter_mm", 0),

            substance_id=data.get("substance_id"),
            coords=data.get("coords"),
            coord_type=data.get("coord_type", 0),

            pressure_mpa=data.get("pressure_mpa", 0),
            phase_state=data.get("phase_state", "ж.ф."),

            spill_coefficient=data.get("spill_coefficient", 1),
            spill_area_m2=data.get("spill_area_m2", 1),
            substance_temperature_c=data.get("substance_temperature_c", 20),
            shutdown_time_s=data.get("shutdown_time_s", 0),
            evaporation_time_s=data.get("evaporation_time_s", 1),

            base_frequency_catastrophic_per_year=data.get("base_frequency_catastrophic_per_year"),
            base_frequency_leak_per_year=data.get("base_frequency_leak_per_year"),
        )


class VesselApparatusEquipment(EquipmentBase):
    """
    Емкостное/аппаратное оборудование.

    equipment_type:
      0 - емкость
      1 - аппарат
      2 - емкость+аппарат

    Параметры:
      - volume_m3: объем, м3
      - fill_fraction: доля заполнения (0..1)

    Частоты (можно None):
      - base_frequency_full_failure_per_year
      - base_frequency_leak_per_year
    """

    ALLOWED_EQUIPMENT_TYPES = (0, 1, 2)

    def __init__(
        self,
        equipment_type: int,
        volume_m3: float,
        fill_fraction: float,

        substance_id: int,
        coords: Optional[Dict[str, Any]],
        coord_type: int,

        pressure_mpa: float,
        phase_state: str,

        spill_coefficient: float,
        spill_area_m2: float,
        substance_temperature_c: float,
        shutdown_time_s: float,
        evaporation_time_s: float,

        base_frequency_full_failure_per_year: Optional[float] = None,
        base_frequency_leak_per_year: Optional[float] = None,
    ):
        super().__init__(
            substance_id=substance_id,
            coords=coords,
            coord_type=coord_type,

            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s,
        )

        self.equipment_type = int(equipment_type)
        self.volume_m3 = float(volume_m3)
        self.fill_fraction = float(fill_fraction)

        self.base_frequency_full_failure_per_year = (
            None if base_frequency_full_failure_per_year is None else float(base_frequency_full_failure_per_year)
        )
        self.base_frequency_leak_per_year = (
            None if base_frequency_leak_per_year is None else float(base_frequency_leak_per_year)
        )

        self._validate_specific()

    def _validate_specific(self) -> None:
        if self.equipment_type not in self.ALLOWED_EQUIPMENT_TYPES:
            raise ValueError("equipment_type должен быть 0 (емкость), 1 (аппарат) или 2 (емкость+аппарат)")
        if self.volume_m3 <= 0:
            raise ValueError("volume_m3 должен быть > 0")
        if not (0 <= self.fill_fraction <= 1):
            raise ValueError("fill_fraction должна быть в диапазоне [0..1]")

    def to_dict(self) -> Dict[str, Any]:
        d = self._common_dict()
        d.update(
            {
                "equipment_class": "VesselApparatusEquipment",
                "equipment_type": self.equipment_type,
                "volume_m3": self.volume_m3,
                "fill_fraction": self.fill_fraction,
                "base_frequency_full_failure_per_year": self.base_frequency_full_failure_per_year,
                "base_frequency_leak_per_year": self.base_frequency_leak_per_year,
            }
        )
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VesselApparatusEquipment":
        return VesselApparatusEquipment(
            equipment_type=data.get("equipment_type", 0),
            volume_m3=data.get("volume_m3", 0),
            fill_fraction=data.get("fill_fraction", 0),

            substance_id=data.get("substance_id"),
            coords=data.get("coords"),
            coord_type=data.get("coord_type", 0),

            pressure_mpa=data.get("pressure_mpa", 0),
            phase_state=data.get("phase_state", "ж.ф."),

            spill_coefficient=data.get("spill_coefficient", 1),
            spill_area_m2=data.get("spill_area_m2", 1),
            substance_temperature_c=data.get("substance_temperature_c", 20),
            shutdown_time_s=data.get("shutdown_time_s", 0),
            evaporation_time_s=data.get("evaporation_time_s", 1),

            base_frequency_full_failure_per_year=data.get("base_frequency_full_failure_per_year"),
            base_frequency_leak_per_year=data.get("base_frequency_leak_per_year"),
        )


# ------------------ Пример использования ------------------

def main() -> None:
    # Пример substance_id (в реальном проекте приходит из SQLite)
    sid = 1

    p = TechPipeline(
        length_m=120.0,
        diameter_mm=100.0,
        wall_thickness_mm=6.0,

        substance_id=sid,
        coords=None,               # можно None: расчет без графики
        coord_type=0,              # линейный

        pressure_mpa=1.6,
        phase_state="ж.ф.",
        spill_coefficient=0.8,
        spill_area_m2=120.0,
        substance_temperature_c=35.0,
        shutdown_time_s=300.0,
        evaporation_time_s=5000.0,  # ограничится до 3600
    )

    nko = PumpCompressorEquipment(
        equipment_type=0,          # насос
        pipeline_diameter_mm=80.0,

        substance_id=sid,
        coords={"x": 10.0, "y": 20.0},
        coord_type=2,              # точечный

        pressure_mpa=0.9,
        phase_state="ж.ф.",
        spill_coefficient=0.7,
        spill_area_m2=60.0,
        substance_temperature_c=25.0,
        shutdown_time_s=120.0,
        evaporation_time_s=800.0,
    )

    v = VesselApparatusEquipment(
        equipment_type=0,          # емкость
        volume_m3=50.0,
        fill_fraction=0.8,

        substance_id=sid,
        coords={"x": 5.0, "y": 7.0},
        coord_type=1,              # стационарный

        pressure_mpa=0.2,
        phase_state="ж.ф.",
        spill_coefficient=0.6,
        spill_area_m2=30.0,
        substance_temperature_c=20.0,
        shutdown_time_s=60.0,
        evaporation_time_s=500.0,
    )

    print("PIPELINE:\n", p.to_dict(), "\n")
    print("NKO:\n", nko.to_dict(), "\n")
    print("VESSEL/APP:\n", v.to_dict(), "\n")


if __name__ == "__main__":
    main()
