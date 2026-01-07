import json
import sqlite3

from calculations.app._liguid_evaporation import evaporation_intensity_kg_m2_s, saturated_vapor_pressure_pa
from calculations.app._lower_concentration import LCLP
from calculations.app._strait_fire import Strait_fire
from calculations.app._tvs_explosion import Explosion
from calculations.app._fatalities_count import count_dead_personal
from calculations.app._injured_count import count_injured_personal
from calculations.app._base_damage_state import damage
from calculations.config import (
    KG_TO_T,
    MASS_IN_CLOUDE,
    MASS_TO_PART,
    MSG,
    WIND,
    SPILL_TO_PART,
    T_TO_KG,
    Pa_TO_kPa,
    P0,
    PEOPLE_COUNT,
)

# Включение/отключение отладочного вывода
DEBUG = True  # True -> печатаем отладку, False -> молчим


def calc_for_scenario(
        equipment: sqlite3.Row,
        substance: sqlite3.Row,
        scenario: dict,
        scenario_no: int,
) -> dict:
    """
    Заглушка расчёта.
    Все неизвестные значения временно = 1
    """

    if DEBUG:
        print("Считаем сценарий:", scenario_no, equipment["equipment_name"])

    result = {}

    # -------------------------------------------------------------------------
    # Обязательные поля
    # -------------------------------------------------------------------------
    result["equipment_id"] = equipment["equipment_id"]
    result["equipment_name"] = equipment["equipment_name"]
    result["hazard_component"] = equipment["hazard_component"]
    result["scenario_no"] = scenario_no

    # -------------------------------------------------------------------------
    # Частоты
    # -------------------------------------------------------------------------
    result["base_frequency"] = scenario.get("base_frequency", 1)
    result["accident_event_probability"] = scenario.get("accident_event_probability", 1)
    result["scenario_frequency"] = scenario.get("scenario_frequency", 1)

    # -------------------------------------------------------------------------
    # Свойства вещества
    # -------------------------------------------------------------------------
    physical = json.loads(substance["physical_json"])
    explosion = json.loads(substance["explosion_json"])

    density_liquid = float(physical["density_liquid_kg_per_m3"])
    density_gas = float(physical["density_gas_kg_per_m3"])
    mol_mass = float(physical["molar_mass_kg_per_mol"])
    t_boiling = float(physical["boiling_point_C"])
    evaporation_heat_J_per_kg = float(physical["evaporation_heat_J_per_kg"])

    # -------------------------------------------------------------------------
    # Количество ОВ
    # -------------------------------------------------------------------------
    volume = equipment["volume_m3"]
    fill_fraction = equipment["fill_fraction"]

    result["amount_t"] = (
        volume * density_liquid * fill_fraction * KG_TO_T
        + volume * density_gas * (1 - fill_fraction) * KG_TO_T
    )

    if DEBUG:
        print(f'result["amount_t"] = {result["amount_t"]}')

    if scenario["scenario_line"] in (1, 2, 3):
        result["ov_in_accident_t"] = result["amount_t"]

    if scenario["scenario_line"] in (4, 5, 6):
        result["ov_in_accident_t"] = result["amount_t"] * MASS_TO_PART

    if DEBUG:
        print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')

    if scenario["scenario_line"] in (1, 4):
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]

    # -------------------------------------------------------------------------
    # Пролив и испарение
    # -------------------------------------------------------------------------
    if scenario["scenario_line"] in (1, 2, 3):
        spill = (
            result["ov_in_accident_t"] * equipment["spill_coefficient"]
            if equipment["spill_area_m2"] == 0
            else equipment["spill_area_m2"]
        )
    else:
        spill = (
            result["ov_in_accident_t"] * equipment["spill_coefficient"]
            if equipment["spill_area_m2"] == 0
            else equipment["spill_area_m2"] * SPILL_TO_PART
        )

    if DEBUG:
        print(f"spill={spill} м2")

    if scenario["scenario_line"] in (2, 5):
        Pn = saturated_vapor_pressure_pa(
            equipment["substance_temperature_c"],
            t_boiling,
            evaporation_heat_J_per_kg,
            mol_mass,
            P0,
        )
        if DEBUG:
            print(f"Pn = {Pn * Pa_TO_kPa} кПа")

        W = evaporation_intensity_kg_m2_s(Pn, mol_mass, eta=1.0)
        m_dot = W * spill

        if DEBUG:
            print(f"m_dot = {m_dot} кг/с")
            print(
                m_dot * equipment["evaporation_time_s"] * KG_TO_T,
                "т испарилось",
            )

        if m_dot * equipment["evaporation_time_s"] * KG_TO_T > result["ov_in_accident_t"]:
            result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
        else:
            result["ov_in_hazard_factor_t"] = (
                m_dot * equipment["evaporation_time_s"] * MASS_IN_CLOUDE * KG_TO_T
            )

    if scenario["scenario_line"] in (3, 6):
        result["ov_in_hazard_factor_t"] = 0

    if DEBUG:
        print(f'result["ov_in_hazard_factor_t"] = {result["ov_in_hazard_factor_t"]}')
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Тепловые потоки
    # -------------------------------------------------------------------------
    result["q_10_5"] = None
    result["q_7_0"] = None
    result["q_4_2"] = None
    result["q_1_4"] = None

    if scenario["scenario_line"] in (1, 4):
        zone = Strait_fire().termal_class_zone(
            S_spill=spill,
            m_sg=MSG,
            mol_mass=mol_mass,
            t_boiling=t_boiling,
            wind_velocity=WIND,
        )

        result["q_10_5"], result["q_7_0"], result["q_4_2"], result["q_1_4"] = map(int, zone)

        if DEBUG:
            print(zone)
            print(20 * "-")

    # -------------------------------------------------------------------------
    # Избыточное давление
    # -------------------------------------------------------------------------
    result["p_70"] = None
    result["p_28"] = None
    result["p_14"] = None
    result["p_5"] = None
    result["p_2"] = None

    if scenario["scenario_line"] in (2,):
        zone = Explosion().explosion_class_zone(
            int(explosion["explosion_hazard_class"]),
            equipment["clutter_degree"],
            result["ov_in_hazard_factor_t"] * T_TO_KG,
            int(explosion["heat_of_combustion_kJ_per_kg"]),
            int(explosion["expansion_degree"]),
            int(explosion["energy_reserve_factor"]),
        )

        result["p_70"], result["p_28"], result["p_14"], result["p_5"], result["p_2"] = map(int, zone[1:6])

        if DEBUG:
            print(zone)
            print(20 * "-")

    # -------------------------------------------------------------------------
    # Зоны поражения
    # -------------------------------------------------------------------------
    result["r_nkpr"] = None
    result["r_vsp"] = None

    if scenario["scenario_line"] in (5,):
        zone = LCLP().lower_concentration_limit(
            result["ov_in_hazard_factor_t"],
            mol_mass,
            t_boiling,
            float(explosion["lel_percent"]),
        )

        result["r_nkpr"], result["r_vsp"] = map(int, zone)

        if DEBUG:
            print(zone)
            print(20 * "-")

    # -------------------------------------------------------------------------
    # Последствия
    # -------------------------------------------------------------------------
    if scenario["scenario_line"] in (1,):
        result["fatalities_count"] = count_dead_personal(result["q_4_2"])
        result["injured_count"] = count_injured_personal(result["q_4_2"])
    elif scenario["scenario_line"] in (2,):
        result["fatalities_count"] = count_dead_personal(result["p_5"])
        result["injured_count"] = count_injured_personal(result["p_5"])
    elif scenario["scenario_line"] in (3, 6):
        result["fatalities_count"] = 0
        result["injured_count"] = 0
    else:
        result["fatalities_count"] = 0
        result["injured_count"] = 1

    if DEBUG:
        print("Погибшие/раненые", result["fatalities_count"], result["injured_count"])
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Ущерб и риски
    # -------------------------------------------------------------------------
    base_damage = damage(
        result["ov_in_accident_t"],
        result["fatalities_count"],
        result["injured_count"],
    )

    result.update(base_damage)

    result["collective_risk_fatalities"] = result["fatalities_count"] * result["scenario_frequency"]
    result["collective_risk_injured"] = result["injured_count"] * result["scenario_frequency"]
    result["expected_value"] = result["total_damage"] * result["scenario_frequency"]

    result["individual_risk_fatalities"] = result["collective_risk_fatalities"] / PEOPLE_COUNT
    result["individual_risk_injured"] = result["collective_risk_injured"] / PEOPLE_COUNT

    return result
