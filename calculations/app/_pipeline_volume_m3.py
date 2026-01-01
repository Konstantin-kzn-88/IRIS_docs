from typing import Optional
import math

def pipeline_internal_volume_m3(
    length_m: Optional[float],
    diameter_mm: Optional[float],
    wall_thickness_mm: Optional[float],
) -> float:
    """Внутренний объем трубы по протяженности и диаметру, исключая толщину стенки."""
    if length_m is None or diameter_mm is None or wall_thickness_mm is None:
        return 0.0

    try:
        L = float(length_m)
        D = float(diameter_mm)
        t = float(wall_thickness_mm)
    except (TypeError, ValueError):
        return 0.0

    d_in_mm = D - 2.0 * t
    if L <= 0 or d_in_mm <= 0:
        return 0.0

    d_in_m = d_in_mm / 1000.0
    area = math.pi * (d_in_m / 2.0) ** 2
    return area * L
