import math
from calculations.config import DENSITY_PEOPLE_PER_M2

def count_injured_personal(radius_m: float) -> int:
    """
    Быстро и детерминированно:
    radius_m — радиус зоны (м)
    density_people_per_m2 — плотность пострадавших (чел/м²),
    обычно > плотности погибших
    Возвращает 0..4
    """
    if radius_m <= 0 or DENSITY_PEOPLE_PER_M2 <= 0:
        return 0

    area = math.pi * radius_m * radius_m
    expected_people = DENSITY_PEOPLE_PER_M2 * area

    injured = int(round(expected_people))

    if injured < 0:
        return 0
    if injured > 4:
        return 4
    return injured