# calculations/app/calculators/scenario_matrix.py

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


# --------------------------------------------------------------
# Загружаем typical_scenarios.json (лежит в calculations/app/scenario/)
# --------------------------------------------------------------

def _load_json() -> dict:
    path = Path(__file__).resolve().parent.parent / "scenario" / "typical_scenarios.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


_raw = _load_json()


# --------------------------------------------------------------
# Автоматическая сборка матрицы (equipment_type, kind) → list of scenarios
# --------------------------------------------------------------

SCENARIO_MATRIX: Dict[tuple, List[dict]] = {}

for eq_str, kinds in _raw["scenarios"].items():
    eq = int(eq_str)

    for kind_str, scen_list in kinds.items():
        kind = int(kind_str)

        key = (eq, kind)
        SCENARIO_MATRIX[key] = []

        for scen in scen_list:
            SCENARIO_MATRIX[key].append(
                {
                    "scenario_line": int(scen["scenario_line"]),
                    "calc_code": int(scen["calc_code"]),
                    "scenario_text": scen["scenario_text"],
                    "scenario_frequency": float(scen["scenario_frequency"]),
                    "base_frequency": float(scen["base_frequency"]),
                    "accident_event_probability": float(scen["accident_event_probability"]),
                }
            )


# --------------------------------------------------------------
# Удобные функции доступа
# --------------------------------------------------------------

def get_scenarios_for_pair(equipment_type: int, kind: int) -> List[dict]:
    """
    Вернуть список словарей:
      [
        {scenario_line, calc_code, scenario_text, ...},
        ...
      ]
    """
    return SCENARIO_MATRIX.get((equipment_type, kind), [])


def get_calc_code(equipment_type: int, kind: int, scenario_line: int) -> Optional[int]:
    """
    Вернуть calc_code для заданных:
        equipment_type
        kind
        scenario_line

    Если такого сценария нет — вернёт None.
    """
    scenarios = SCENARIO_MATRIX.get((equipment_type, kind), [])
    for scen in scenarios:
        if scen["scenario_line"] == scenario_line:
            return scen["calc_code"]
    return None
