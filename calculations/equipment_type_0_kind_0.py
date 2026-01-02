import json
import sqlite3

from calculations.app._liguid_evaporation import (
    evaporation_intensity_kg_m2_s,
    saturated_vapor_pressure_pa,
)
from calculations.app._liquid_flow import liquid_leak_mass_flow
from calculations.app._lower_concentration import LCLP
from calculations.app._pipeline_volume_m3 import pipeline_internal_volume_m3
from calculations.app._strait_fire import Strait_fire
from calculations.app._tvs_explosion import Explosion
from calculations.config import KG_TO_T, MASS_IN_CLOUDE, MASS_TO_PART, MSG, WIND, SPILL_TO_PART, T_TO_KG, Pa_TO_kPa, P0


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
    # Частоты (из json, если есть)
    # -------------------------------------------------------------------------
    result["base_frequency"] = scenario.get("base_frequency", 1)
    result["accident_event_probability"] = scenario.get("accident_event_probability", 1)

    # Умножаем на длину, т.к. трубопровод
    result["scenario_frequency"] = scenario.get("scenario_frequency", 1) * equipment["length_m"]

    # -------------------------------------------------------------------------
    # Физические свойства / взрывопожарные свойства (из substances.json)
    # -------------------------------------------------------------------------
    physical = json.loads(substance["physical_json"])
    explosion = json.loads(substance["explosion_json"])

    density = float(physical["density_liquid_kg_per_m3"])
    mol_mass = float(physical["molar_mass_kg_per_mol"])
    t_boiling = float(physical["boiling_point_C"])
    evaporation_heat_J_per_kg = float(physical["evaporation_heat_J_per_kg"])

    # -------------------------------------------------------------------------
    # Количество ОВ
    # -------------------------------------------------------------------------
    pipeline_volume = pipeline_internal_volume_m3(
        equipment["length_m"],
        equipment["diameter_mm"],
        equipment["wall_thickness_mm"],
    )

    result["amount_t"] = pipeline_volume * density * KG_TO_T

    print(f'result["amount_t"] = {result["amount_t"]}')

    if scenario["scenario_line"] in (1, 2, 3):  # пролив полная
        result["ov_in_accident_t"] = result["amount_t"] + liquid_leak_mass_flow(
            equipment["pressure_mpa"],
            equipment["diameter_mm"],
            density,
        ) * KG_TO_T

    if scenario["scenario_line"] in (4, 5, 6):  # пролив частичная
        result["ov_in_accident_t"] = (
                                             result["amount_t"]
                                             + liquid_leak_mass_flow(
                                         equipment["pressure_mpa"],
                                         equipment["diameter_mm"],
                                         density,
                                     ) * KG_TO_T
                                     ) * MASS_TO_PART

    print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')

    if scenario["scenario_line"] in (1, 4):  # пролив полная/частичная
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]

    # -------------------------------------------------------------------------
    # Параметры пролива и расчет испарения вещества
    # -------------------------------------------------------------------------
    if scenario["scenario_line"] in (1, 2, 3):  # пролив полная
        if equipment["spill_area_m2"] == 0:
            spill = result["ov_in_accident_t"] * equipment["spill_coefficient"]
        else:
            spill = equipment["spill_area_m2"]
    else:
        if equipment["spill_area_m2"] == 0:
            spill = result["ov_in_accident_t"] * equipment["spill_coefficient"]
        else:
            spill = equipment["spill_area_m2"] * SPILL_TO_PART

    print(f'spill={spill} м2')

    if scenario["scenario_line"] in (2, 5):  # испарение для взрыва и вспышки
        Tk = equipment["substance_temperature_c"]
        Tp = t_boiling
        M = mol_mass

        Pn = saturated_vapor_pressure_pa(equipment["substance_temperature_c"], t_boiling, evaporation_heat_J_per_kg, mol_mass, P0)
        print(f'Pn = {Pn * Pa_TO_kPa} кПа')
        W = evaporation_intensity_kg_m2_s(Pn, M, eta=1.0)

        m_dot = W * spill  # кг/с

        print(f'm_dot = {m_dot} кг/с')
        print(
            f'm_dot * equipment["evaporation_time_s"] * KG_TO_T = {m_dot * equipment["evaporation_time_s"] * KG_TO_T} т')

        # Проверяем не испарилось ли больше чем вылилось
        if m_dot * equipment["evaporation_time_s"] * KG_TO_T > result["ov_in_accident_t"]:
            result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
        else:
            result["ov_in_hazard_factor_t"] = m_dot * equipment["evaporation_time_s"] * MASS_IN_CLOUDE * KG_TO_T

    if scenario["scenario_line"] in (3, 6):  # ликвидация
        result["ov_in_hazard_factor_t"] = 0

    print(f'result["ov_in_hazard_factor_t"] = {result["ov_in_hazard_factor_t"]}')
    print(20 * "-")

    # -------------------------------------------------------------------------
    # Тепловые потоки
    # -------------------------------------------------------------------------
    result["q_10_5"] = None
    result["q_7_0"] = None
    result["q_4_2"] = None
    result["q_1_4"] = None

    if scenario["scenario_line"] in (1, 4):  # пролив полная/частичная
        zone = Strait_fire().termal_class_zone(
            S_spill=spill,
            m_sg=MSG,
            mol_mass=mol_mass,
            t_boiling=t_boiling,
            wind_velocity=WIND,
        )

        result["q_10_5"] = int(zone[0])
        result["q_7_0"] = int(zone[1])
        result["q_4_2"] = int(zone[2])
        result["q_1_4"] = int(zone[3])

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

    if scenario["scenario_line"] in (2,):  # взрыв
        class_substance = int(explosion["explosion_hazard_class"])
        heat_of_combustion = int(explosion["heat_of_combustion_kJ_per_kg"])
        sigma = int(explosion["expansion_degree"])
        energy_level = int(explosion["energy_reserve_factor"])
        view_space = equipment["clutter_degree"]
        mass = result["ov_in_hazard_factor_t"] * T_TO_KG

        zone = Explosion().explosion_class_zone(
            class_substance,
            view_space,
            mass,
            heat_of_combustion,
            sigma,
            energy_level,
        )

        result["p_70"] = int(zone[1])
        result["p_28"] = int(zone[2])
        result["p_14"] = int(zone[3])
        result["p_5"] = int(zone[4])
        result["p_2"] = int(zone[5])

        print(zone)
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Зоны поражения
    # -------------------------------------------------------------------------
    result["l_f"] = None
    result["d_f"] = None

    result["r_nkpr"] = None
    result["r_vsp"] = None

    if scenario["scenario_line"] in (5,):  # вспышка
        mass = result["ov_in_hazard_factor_t"]
        lower_concentration = float(explosion["lel_percent"])

        zone = LCLP().lower_concentration_limit(mass, mol_mass, t_boiling, lower_concentration)

        result["r_nkpr"] = int(zone[0])
        result["r_vsp"] = int(zone[1])

        print(zone)
        print(20 * "-")

    result["l_pt"] = None
    result["p_pt"] = None

    # -------------------------------------------------------------------------
    # Токсическое воздействие
    # -------------------------------------------------------------------------
    result["q_600"] = None
    result["q_320"] = None
    result["q_220"] = None
    result["q_120"] = None

    result["s_t"] = None

    # -------------------------------------------------------------------------
    # Последствия
    # -------------------------------------------------------------------------
    result["fatalities_count"] = None
    result["injured_count"] = None

    # -------------------------------------------------------------------------
    # Ущерб
    # -------------------------------------------------------------------------
    result["direct_losses"] = 1
    result["liquidation_costs"] = 1
    result["social_losses"] = 1
    result["indirect_damage"] = 1
    result["total_environmental_damage"] = 1
    result["total_damage"] = 1

    # -------------------------------------------------------------------------
    # Риски
    # -------------------------------------------------------------------------
    result["collective_risk_fatalities"] = 1
    result["collective_risk_injured"] = 1
    result["expected_value"] = 1

    result["individual_risk_fatalities"] = 1
    result["individual_risk_injured"] = 1

    return result
