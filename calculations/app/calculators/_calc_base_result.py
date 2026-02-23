import sqlite3
from typing import Any


def init_result_base(
    equipment: sqlite3.Row,
    scenario: dict,
    scenario_no: int,
) -> dict:
    """
    Единая инициализация обязательных полей + частоты.
    ВНИМАНИЕ: сохраняем прежнюю семантику — scenario_frequency умножаем на quantity_equipment.
    """
    r: dict[str, Any] = {}

    # обязательные поля
    r["equipment_id"] = equipment["equipment_id"]
    r["equipment_name"] = equipment["equipment_name"]
    r["hazard_component"] = equipment["hazard_component"]
    r["scenario_no"] = scenario_no

    # частоты
    r["base_frequency"] = scenario.get("base_frequency", 1)
    r["accident_event_probability"] = scenario.get("accident_event_probability", 1)
    r["scenario_frequency"] = scenario.get("scenario_frequency", 1) * equipment["quantity_equipment"]

    return r