# models/equipment/equipment_model.py

# Допустимые значения фазового состояния (строго по вашему формату)
ALLOWED_PHASE_STATES = ("ж.ф.", "г.ф.", "ж.ф.+г.ф.")

# Тип расположения: 0-линейный, 1-стационарный, 2-другое (оставим как вы указали)
ALLOWED_COORD_TYPES = (0, 1, 2)

# Тип оборудования:
# 0-трубопровод, 1-РВС, 2-аппарат под давлением, 3-колонна, 4-насос,
# 5-компрессор, 6-теплообменник, 7-цистерна
EQUIPMENT_TYPES = (0, 1, 2, 3, 4, 5, 6, 7)


class Equipment:
    def __init__(
        self,
        id=None,
        substance_id=None,

        phase_state="ж.ф.",
        coord_type=1,
        equipment_type=0,

        coordinates=None,

        length_m=None,
        diameter_mm=None,
        wall_thickness_mm=None,
        volume_m3=None,
        fill_fraction=None,           # 0..1

        pressure_mpa=None,

        spill_coefficient=None,
        spill_area_m2=None,
        substance_temperature_c=None,
        shutdown_time_s=None,
        evaporation_time_s=None,      # <= 3600
    ):
        self.id = id
        self.substance_id = substance_id

        self.phase_state = phase_state
        self.coord_type = coord_type
        self.equipment_type = equipment_type

        # список координат: [x1, y1, x2, y2, ...]
        self.coordinates = coordinates if coordinates is not None else []

        self.length_m = length_m
        self.diameter_mm = diameter_mm
        self.wall_thickness_mm = wall_thickness_mm
        self.volume_m3 = volume_m3
        self.fill_fraction = fill_fraction

        self.pressure_mpa = pressure_mpa

        self.spill_coefficient = spill_coefficient
        self.spill_area_m2 = spill_area_m2
        self.substance_temperature_c = substance_temperature_c
        self.shutdown_time_s = shutdown_time_s
        self.evaporation_time_s = evaporation_time_s
