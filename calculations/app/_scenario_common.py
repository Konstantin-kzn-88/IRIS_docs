# calculations/app/_scenario_common.py
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable

from core.config import PEOPLE_COUNT


@dataclass(frozen=True)
class SubstanceProps:
    physical: dict[str, Any]
    explosion: dict[str, Any]

    density_liquid: float
    density_gas: float
    mol_mass: float
    t_boiling: float
    evaporation_heat_J_per_kg: float


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


def parse_substance_props(substance: sqlite3.Row) -> SubstanceProps:
    """
    Единый парсинг physical_json / explosion_json + приведение типов.
    Устойчиво к None в полях, которые для газа/жидкости могут быть неприменимы.
    """
    physical = json.loads(substance["physical_json"])
    explosion = json.loads(substance["explosion_json"])

    def _f(value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    boiling_raw = physical.get("boiling_point_C")
    t_boiling = _f(boiling_raw, default=0.0)

    return SubstanceProps(
        physical=physical,
        explosion=explosion,
        density_liquid=_f(physical.get("density_liquid_kg_per_m3"), default=0.0),
        density_gas=_f(physical.get("density_gas_kg_per_m3"), default=0.0),
        mol_mass=_f(physical.get("molar_mass_kg_per_mol"), default=0.0),
        t_boiling=t_boiling,
        evaporation_heat_J_per_kg=_f(physical.get("evaporation_heat_J_per_kg"), default=0.0),
    )


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


def apply_damage_block(
    result: dict,
    scenario: dict,
    *,
    damage_coeffs: list[float],
    damage_func: Callable[[float, int, int], dict],
) -> None:
    """
    Унифицированный блок ущерба:
    - выбираем k по scenario_line
    - считаем mass_for_damage = k * amount_t
    - вызываем damage()
    - раскладываем по полям result
    """
    # дефолты на всякий случай
    result.setdefault("direct_losses", None)
    result.setdefault("liquidation_costs", None)
    result.setdefault("social_losses", None)
    result.setdefault("indirect_damage", None)
    result.setdefault("total_environmental_damage", None)
    result.setdefault("total_damage", None)

    sc_line = int(scenario.get("scenario_line", 0))
    if 1 <= sc_line <= len(damage_coeffs):
        k = float(damage_coeffs[sc_line - 1])
    else:
        k = 0.0

    amount_t = float(result.get("amount_t", 0.0))
    mass_for_damage = k * amount_t

    base_damage = damage_func(
        mass_for_damage,
        int(result.get("fatalities_count", 0) or 0),
        int(result.get("injured_count", 0) or 0),
    )

    result["direct_losses"] = base_damage["direct_losses"]
    result["liquidation_costs"] = base_damage["liquidation_costs"]
    result["social_losses"] = base_damage["social_losses"]
    result["indirect_damage"] = base_damage["indirect_damage"]
    result["total_environmental_damage"] = base_damage["total_environmental_damage"]
    result["total_damage"] = base_damage["total_damage"]


def apply_risk_block(result: dict) -> None:
    """
    Унифицированный блок рисков (как у тебя везде):
    collective_* = count * scenario_frequency
    individual_* = collective / PEOPLE_COUNT
    expected_value = total_damage * scenario_frequency
    """
    result["collective_risk_fatalities"] = (result["fatalities_count"] or 0) * result["scenario_frequency"]
    result["collective_risk_injured"] = (result["injured_count"] or 0) * result["scenario_frequency"]
    result["expected_value"] = (result["total_damage"] or 0) * result["scenario_frequency"]

    result["individual_risk_fatalities"] = result["collective_risk_fatalities"] / PEOPLE_COUNT
    result["individual_risk_injured"] = result["collective_risk_injured"] / PEOPLE_COUNT