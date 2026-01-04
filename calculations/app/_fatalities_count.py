import math
from calculations.config import DENSITY_PEOPLE_PER_M2

def count_dead_personal(radius_m: float) -> int:


    """
    Быстро и детерминированно:
    radius_m — радиус зоны (м)
    density_people_per_m2 — плотность людей (чел/м²)
    Возвращает 0..3
    """
    if radius_m <= 0 or DENSITY_PEOPLE_PER_M2 <= 0:
        return 0

    area = math.pi * radius_m * radius_m
    expected_people = DENSITY_PEOPLE_PER_M2 * area

    # детерминированная дискретизация + ограничение "не больше 3"
    dead = int(round(expected_people))

    if dead < 0:
        return 0
    if dead > 3:
        return 3
    return dead
