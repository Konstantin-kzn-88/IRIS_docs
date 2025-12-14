# file: equipment_entities.py

class EquipmentBase:
    """
    Базовый класс оборудования.
    Содержит общие параметры сценария пролива/испарения + давление + фазовое состояние.
    """

    # Допустимые значения фазового состояния (строго по вашему формату)
    ALLOWED_PHASE_STATES = ("ж.ф.", "г.ф.", "ж.ф.+г.ф.")

    def __init__(self,
                 pressure_mpa,
                 phase_state,

                 spill_coefficient,
                 spill_area_m2,
                 substance_temperature_c,
                 shutdown_time_s,
                 evaporation_time_s):

        # Давление, МПа
        self.pressure_mpa = float(pressure_mpa)

        # Фазовое состояние: "ж.ф." / "г.ф." / "ж.ф.+г.ф."
        self.phase_state = str(phase_state).strip()

        # Коэффициент пролива, -
        self.spill_coefficient = float(spill_coefficient)

        # Площадь пролива, м2
        self.spill_area_m2 = float(spill_area_m2)

        # Температура вещества, °C
        self.substance_temperature_c = float(substance_temperature_c)

        # Время отключения, с
        self.shutdown_time_s = float(shutdown_time_s)

        # Время испарения, с (ограничивается сверху 3600 с)
        self.evaporation_time_s = self._limit_evaporation_time(evaporation_time_s)

        # Проверка общих параметров
        self._validate_common_parameters()

    def _limit_evaporation_time(self, evaporation_time_s):
        """Ограничение времени испарения: не более 3600 с."""
        evaporation_time_s = float(evaporation_time_s)
        if evaporation_time_s > 3600.0:
            return 3600.0
        return evaporation_time_s

    def _validate_common_parameters(self):
        """Проверка общих параметров сценария."""
        if self.pressure_mpa < 0:
            raise ValueError("pressure_mpa (давление) не может быть отрицательным")

        if self.phase_state not in self.ALLOWED_PHASE_STATES:
            raise ValueError(
                'phase_state должен быть одним из: "ж.ф.", "г.ф.", "ж.ф.+г.ф."'
            )

        if self.spill_coefficient < 0:
            raise ValueError("spill_coefficient не может быть отрицательным")

        if self.spill_area_m2 <= 0:
            raise ValueError("spill_area_m2 должна быть > 0")

        if self.shutdown_time_s < 0:
            raise ValueError("shutdown_time_s не может быть отрицательным")

        if self.evaporation_time_s <= 0:
            raise ValueError("evaporation_time_s должна быть > 0")

    def _common_dict(self):
        """Словарь общих полей — чтобы не дублировать в наследниках."""
        return {
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

    Табличные частоты по DN:
      DN < 75 мм: rupture 1e-6, leak 5e-6
      75..150 мм: rupture 3e-7, leak 2e-6
      DN > 150 мм: rupture 1e-7, leak 5e-7
    """

    def __init__(self,
                 length_m,
                 diameter_mm,
                 wall_thickness_mm,

                 pressure_mpa,
                 phase_state,

                 spill_coefficient,
                 spill_area_m2,
                 substance_temperature_c,
                 shutdown_time_s,
                 evaporation_time_s,

                 base_frequency_rupture_per_year=None,
                 base_frequency_depressurization_per_year=None):

        # Инициализация общих параметров
        super().__init__(
            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s
        )

        # Специфичные параметры трубопровода
        self.length_m = float(length_m)                 # м
        self.diameter_mm = float(diameter_mm)           # мм
        self.wall_thickness_mm = float(wall_thickness_mm)  # мм

        self._validate_geometry()

        # Табличные частоты по диаметру
        rupture_freq, leak_freq = self._get_base_frequencies_by_diameter(self.diameter_mm)

        self.base_frequency_rupture_per_year = float(
            base_frequency_rupture_per_year
            if base_frequency_rupture_per_year is not None
            else rupture_freq
        )

        self.base_frequency_depressurization_per_year = float(
            base_frequency_depressurization_per_year
            if base_frequency_depressurization_per_year is not None
            else leak_freq
        )

    def _validate_geometry(self):
        if self.length_m <= 0:
            raise ValueError("length_m должна быть > 0")

        if self.diameter_mm <= 0:
            raise ValueError("diameter_mm должна быть > 0")

        if self.wall_thickness_mm <= 0:
            raise ValueError("wall_thickness_mm должна быть > 0")

        if self.wall_thickness_mm >= (self.diameter_mm / 2.0):
            raise ValueError("wall_thickness_mm слишком большая относительно диаметра")

    def _get_base_frequencies_by_diameter(self, diameter_mm):
        if diameter_mm < 75.0:
            return 1e-6, 5e-6
        elif diameter_mm <= 150.0:
            return 3e-7, 2e-6
        else:
            return 1e-7, 5e-7

    def get_effective_hole_diameter_mm(self):
        """0.1*DN, но не более 50 мм."""
        hole = 0.1 * self.diameter_mm
        return 50.0 if hole > 50.0 else hole

    def to_dict(self):
        data = {
            "equipment_class": "TechPipeline",
            "length_m": self.length_m,
            "diameter_mm": self.diameter_mm,
            "wall_thickness_mm": self.wall_thickness_mm,
            "base_frequency_rupture_per_year": self.base_frequency_rupture_per_year,
            "base_frequency_depressurization_per_year": self.base_frequency_depressurization_per_year,
            "effective_hole_diameter_mm": self.get_effective_hole_diameter_mm(),
        }
        data.update(self._common_dict())
        return data


class PumpCompressorEquipment(EquipmentBase):
    """
    Насосно-компрессорное оборудование (НКО).

    Тип:
      0 - Центробежные насосы герметичные
      1 - Центробежные насосы с уплотнениями
      2 - Поршневые насосы
      3 - Компрессоры

    Частоты:
      Тип 0: catastrophic 1e-5, leak 5e-5
      Тип 1: catastrophic 1e-4, leak 4.4e-3
      Тип 2: catastrophic 1e-4, leak 4.4e-3
      Тип 3: catastrophic 1e-4, leak 4.4e-3
    """

    TYPE_NAMES = {
        0: "Центробежные насосы герметичные",
        1: "Центробежные насосы с уплотнениями",
        2: "Поршневые насосы",
        3: "Компрессоры",
    }

    def __init__(self,
                 equipment_type,
                 pipeline_diameter_mm,

                 pressure_mpa,
                 phase_state,

                 spill_coefficient,
                 spill_area_m2,
                 substance_temperature_c,
                 shutdown_time_s,
                 evaporation_time_s,

                 base_frequency_catastrophic_per_year=None,
                 base_frequency_leak_per_year=None):

        super().__init__(
            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s
        )

        self.equipment_type = int(equipment_type)
        self.pipeline_diameter_mm = float(pipeline_diameter_mm)

        self._validate_specific()

        cat_freq, leak_freq = self._get_base_frequencies_by_type(self.equipment_type)

        self.base_frequency_catastrophic_per_year = float(
            base_frequency_catastrophic_per_year
            if base_frequency_catastrophic_per_year is not None
            else cat_freq
        )
        self.base_frequency_leak_per_year = float(
            base_frequency_leak_per_year
            if base_frequency_leak_per_year is not None
            else leak_freq
        )

    def _validate_specific(self):
        if self.equipment_type not in self.TYPE_NAMES:
            raise ValueError("equipment_type должен быть 0, 1, 2 или 3")

        if self.pipeline_diameter_mm <= 0:
            raise ValueError("pipeline_diameter_mm должен быть > 0")

    def _get_base_frequencies_by_type(self, equipment_type):
        if equipment_type == 0:
            return 1e-5, 5e-5
        else:
            return 1e-4, 4.4e-3

    def get_equipment_type_name(self):
        return self.TYPE_NAMES[self.equipment_type]

    def get_effective_hole_diameter_mm(self):
        """0.1*DN, но не более 50 мм."""
        hole = 0.1 * self.pipeline_diameter_mm
        return 50.0 if hole > 50.0 else hole

    def to_dict(self):
        data = {
            "equipment_class": "PumpCompressorEquipment",
            "equipment_type": self.equipment_type,
            "equipment_type_name": self.get_equipment_type_name(),
            "pipeline_diameter_mm": self.pipeline_diameter_mm,
            "base_frequency_catastrophic_per_year": self.base_frequency_catastrophic_per_year,
            "base_frequency_leak_per_year": self.base_frequency_leak_per_year,
            "effective_hole_diameter_mm": self.get_effective_hole_diameter_mm(),
        }
        data.update(self._common_dict())
        return data


class VesselApparatusEquipment(EquipmentBase):
    """
    Аппаратурное оборудование (сосуды/аппараты/реакторы).

    Тип:
      0 - Сосуды хранения под давлением
      1 - Технологические аппараты
      2 - Химические реакторы
      3 - Одностенный резервуар
      4 - Теплообменник
      5 - Цистерна под избыточным давлением
      6 - Цистерна при атмосферном давлении

    Частоты:
      Тип 0: full_failure 1e-6, leak(10mm) 1e-5
      Тип 1: full_failure 1e-5, leak(10mm) 1e-4
      Тип 2: full_failure 1e-5, leak(10mm) 1e-4
      Тип 3: full_failure 1e-5, leak(10mm) 1e-4
      Тип 4: full_failure 1e-4, leak(10mm) 1e-3
      Тип 5: full_failure 5e-7, leak(10mm) 5e-7
      Тип 6: full_failure 5e-5, leak(10mm) 5e-7

    Для истечения отверстие фиксировано 10 мм.
    """

    TYPE_NAMES = {
        0: "Сосуды хранения под давлением",
        1: "Технологические аппараты",
        2: "Химические реакторы",
        3: "Одностенный резервуар",
        4: "Теплообменник",
        5: "Цистерна под избыточным давлением",
        6: "Цистерна при атмосферном давлении",
    }

    def __init__(self,
                 equipment_type,
                 volume_m3,
                 fill_fraction,

                 pressure_mpa,
                 phase_state,

                 spill_coefficient,
                 spill_area_m2,
                 substance_temperature_c,
                 shutdown_time_s,
                 evaporation_time_s,

                 base_frequency_full_failure_per_year=None,
                 base_frequency_leak_per_year=None):

        super().__init__(
            pressure_mpa=pressure_mpa,
            phase_state=phase_state,

            spill_coefficient=spill_coefficient,
            spill_area_m2=spill_area_m2,
            substance_temperature_c=substance_temperature_c,
            shutdown_time_s=shutdown_time_s,
            evaporation_time_s=evaporation_time_s
        )

        self.equipment_type = int(equipment_type)
        self.volume_m3 = float(volume_m3)
        self.fill_fraction = float(fill_fraction)

        self._validate_specific()

        full_freq, leak_freq = self._get_base_frequencies_by_type(self.equipment_type)

        self.base_frequency_full_failure_per_year = float(
            base_frequency_full_failure_per_year
            if base_frequency_full_failure_per_year is not None
            else full_freq
        )
        self.base_frequency_leak_per_year = float(
            base_frequency_leak_per_year
            if base_frequency_leak_per_year is not None
            else leak_freq
        )

        # По таблице: эффективный диаметр отверстия фиксирован 10 мм
        self.effective_hole_diameter_mm = 10.0

    def _validate_specific(self):
        if self.equipment_type not in self.TYPE_NAMES:
            raise ValueError("equipment_type должен быть 0..6")

        if self.volume_m3 <= 0:
            raise ValueError("volume_m3 должен быть > 0")

        if not (0.0 <= self.fill_fraction <= 1.0):
            raise ValueError("fill_fraction должна быть в диапазоне 0..1")

    def _get_base_frequencies_by_type(self, equipment_type):
        """
        Возвращает:
          (частота полного разрушения, частота истечения через отверстие 10 мм), 1/год
        """
        if equipment_type == 0:
            return 1e-6, 1e-5

        if equipment_type in (1, 2, 3):
            return 1e-5, 1e-4

        if equipment_type == 4:
            return 1e-4, 1e-3

        if equipment_type == 5:
            return 5e-7, 5e-7

        if equipment_type == 6:
            return 5e-5, 5e-7

        raise ValueError("Неизвестный equipment_type для расчета частот")

    def get_equipment_type_name(self):
        return self.TYPE_NAMES[self.equipment_type]

    def get_filled_volume_m3(self):
        """Заполненный объём, м3."""
        return self.volume_m3 * self.fill_fraction

    def to_dict(self):
        data = {
            "equipment_class": "VesselApparatusEquipment",
            "equipment_type": self.equipment_type,
            "equipment_type_name": self.get_equipment_type_name(),
            "volume_m3": self.volume_m3,
            "fill_fraction": self.fill_fraction,
            "filled_volume_m3": self.get_filled_volume_m3(),
            "base_frequency_full_failure_per_year": self.base_frequency_full_failure_per_year,
            "base_frequency_leak_per_year": self.base_frequency_leak_per_year,
            "effective_hole_diameter_mm": self.effective_hole_diameter_mm,
        }
        data.update(self._common_dict())
        return data


def main():
    # 1) Трубопровод
    p = TechPipeline(
        length_m=120.0,
        diameter_mm=100.0,
        wall_thickness_mm=6.0,

        pressure_mpa=1.6,
        phase_state="ж.ф.",

        spill_coefficient=0.8,
        spill_area_m2=120.0,
        substance_temperature_c=35.0,
        shutdown_time_s=300.0,
        evaporation_time_s=5000.0,  # ограничится до 3600
    )

    # 2) НКО: компрессор
    nko = PumpCompressorEquipment(
        equipment_type=3,
        pipeline_diameter_mm=200.0,

        pressure_mpa=2.5,
        phase_state="г.ф.",

        spill_coefficient=0.8,
        spill_area_m2=120.0,
        substance_temperature_c=35.0,
        shutdown_time_s=300.0,
        evaporation_time_s=5000.0,  # ограничится до 3600
    )

    # 3) Аппарат: технологический (тип 1)
    v = VesselApparatusEquipment(
        equipment_type=1,
        volume_m3=25.0,
        fill_fraction=0.7,

        pressure_mpa=0.3,
        phase_state="ж.ф.+г.ф.",

        spill_coefficient=0.8,
        spill_area_m2=120.0,
        substance_temperature_c=35.0,
        shutdown_time_s=300.0,
        evaporation_time_s=5000.0,  # ограничится до 3600
    )

    print("PIPELINE:\n", p.to_dict(), "\n")
    print("NKO:\n", nko.to_dict(), "\n")
    print("VESSEL/APP:\n", v.to_dict(), "\n")


if __name__ == "__main__":
    main()
