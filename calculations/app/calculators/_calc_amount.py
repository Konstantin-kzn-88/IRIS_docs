# calculations/app/calculators/_calc_amount.py
import sqlite3
from typing import Dict, Any

# Импорты твоих уже существующих расчётных модулей
from calculations.app._pipeline_volume_m3 import pipeline_internal_volume_m3
from calculations.app._liquid_flow import liquid_leak_mass_flow
from calculations.app._scenario_common import parse_substance_props
from core.config import KG_TO_T


def calculate_amount(equipment_type: int, kind: int, equipment: sqlite3.Row, substance: sqlite3.Row) -> Dict[
    str, float]:
    """
    Унифицированный расчет массы опасного вещества
    для любого equipment_type и kind.

    Возвращает:
        {
            "amount_t": ..., - количество опасного вещества в оборудовании
            "ov_in_accident_t": ..., - количество опасного вещества в аварии
        }
    """

    # -------------------------------------------------------------------------
    # Свойства вещества
    # -------------------------------------------------------------------------
    props = parse_substance_props(substance)
    density = float(props.physical["density_liquid_kg_per_m3"])

    # ---------------------------------------------------------
    # 0. Базовые значения (по умолчанию)
    # ---------------------------------------------------------
    result = {
        "amount_t": 0.0,
        "ov_in_accident_t": 0.0,
    }

    # ---------------------------------------------------------
    # 1. ТРУБОПРОВОД
    # ---------------------------------------------------------
    if equipment_type == 0:
        # Жидкость (пока ЛВЖ)
        if kind == 0:
            # 1.1 Полный объем участка трубопровода
            pipeline_volume = pipeline_internal_volume_m3(
                equipment["length_m"],
                equipment["diameter_mm"],
                equipment["wall_thickness_mm"],
            )
            result["amount_t"] = pipeline_volume * density * KG_TO_T

            # 1.2 Масса, вышедшая в аварию

            result["ov_in_accident_t"] = result["amount_t"] + liquid_leak_mass_flow(
                equipment["pressure_mpa"],
                equipment["diameter_mm"],
                density,
            ) * equipment["shutdown_time_s"] * KG_TO_T

        return result

    # ---------------------------------------------------------
    # 2. Резервуар, колонна, теплообменник и т.д.
    # ---------------------------------------------------------
    # Здесь просто добавим шаблон, который потом наполним
    # для всех остальных equipment_type
    # ---------------------------------------------------------

    elif equipment_type in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        # временно
        pass
        return result

    # ---------------------------------------------------------
    # 3. На крайний случай
    # ---------------------------------------------------------
    return result
