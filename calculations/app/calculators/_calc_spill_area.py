import sqlite3


def calc_spill_area_m2(
    ov_in_accident_t: float,
    equipment: sqlite3.Row,
    *,
    is_full_spill: bool,
    spill_to_part: float,
) -> float:
    """
    Унифицируем кусок:
      spill = ov * spill_coefficient, если spill_area_m2 == 0
      иначе spill_area_m2 (полный пролив) или spill_area_m2 * SPILL_TO_PART (частичный)
    """
    if equipment["spill_area_m2"] == 0:
        return ov_in_accident_t * equipment["spill_coefficient"]
    return float(equipment["spill_area_m2"]) if is_full_spill else float(equipment["spill_area_m2"]) * spill_to_part
