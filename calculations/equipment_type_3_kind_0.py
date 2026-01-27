import json
import sqlite3

from calculations.app._liguid_evaporation import evaporation_intensity_kg_m2_s, saturated_vapor_pressure_pa
from calculations.app._liquid_flow import liquid_leak_mass_flow
from calculations.app._gas_flow import gas_leak_mass_flow
from calculations.app._lower_concentration import LCLP
from calculations.app._strait_fire import Strait_fire
from calculations.app._tvs_explosion import Explosion
from calculations.app._jet_fire import Torch
from calculations.app._fireball import Fireball
from calculations.app._base_damage_state import damage
from core.config import KG_TO_T, MASS_IN_CLOUDE, MSG, WIND, SPILL_TO_PART, T_TO_KG, Pa_TO_kPa, P0, \
    PEOPLE_COUNT, D_MM_JET_LIQUID, D_MM_JET_GAS, MASS_IN_BLEVE, EF, DAMAGE_NINE_SC

# Включение/отключение отладочного вывода
DEBUG = False  # True -> печатаем отладку, False -> молчим


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

    # print("Считаем сценарий:", scenario_no, equipment["equipment_name"])
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
    # Частоты (из json, если есть)
    # -------------------------------------------------------------------------
    result["base_frequency"] = scenario.get("base_frequency", 1)
    result["accident_event_probability"] = scenario.get("accident_event_probability", 1)

    # Надо умножить частоту на количество оборудования
    result["scenario_frequency"] = scenario.get("scenario_frequency", 1) * equipment["quantity_equipment"]

    # -------------------------------------------------------------------------
    # Физические свойства / взрывопожарные свойства (из substances.json)
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

    result["amount_t"] = volume * density_liquid * fill_fraction * KG_TO_T + volume * density_gas * (
            1 - fill_fraction) * KG_TO_T

    # print(f'result["amount_t"] = {result["amount_t"]}')
    if DEBUG:
        print(f'result["amount_t"] = {result["amount_t"]}')

    if scenario["scenario_line"] in (1, 2, 3, 9):  # авария полная
        result["ov_in_accident_t"] = result["amount_t"]

    if scenario["scenario_line"] in (4, 5):  # авария частичная (ниже уровня жидкости)
        liquid_flow = liquid_leak_mass_flow(equipment["pressure_mpa"], D_MM_JET_LIQUID, density_liquid)
        result["ov_in_accident_t"] = liquid_flow * equipment["shutdown_time_s"] * KG_TO_T

    if scenario["scenario_line"] in (6, 7, 8):  # авария частичная (выше уровня жидкости)
        gas_flow = gas_leak_mass_flow(equipment["pressure_mpa"], D_MM_JET_GAS, equipment["substance_temperature_c"],
                                      mol_mass)
        result["ov_in_accident_t"] = gas_flow * equipment["shutdown_time_s"] * KG_TO_T

    # print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')
    if DEBUG:
        print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')

    # -------------------------------------------------------------------------
    # Количество вещества участвующего в создании поражающего фактора
    # -------------------------------------------------------------------------
    if scenario["scenario_line"] in (1,):  # авария полная/частичная
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

    # print(f'spill={spill} м2')
    if DEBUG:
        print(f'spill={spill} м2')

    if scenario["scenario_line"] in (2,):  # испарение для взрыва

        Pn = saturated_vapor_pressure_pa(equipment["substance_temperature_c"], t_boiling, evaporation_heat_J_per_kg,
                                         mol_mass, P0)
        # print(f'Pn = {Pn * Pa_TO_kPa} кПа')
        if DEBUG:
            print(f'Pn = {Pn * Pa_TO_kPa} кПа')

        W = evaporation_intensity_kg_m2_s(Pn, mol_mass, eta=1.0)

        m_dot = W * spill  # кг/с

        # print(f'm_dot = {m_dot} кг/с')
        # print(
        #     f'm_dot * equipment["evaporation_time_s"] * KG_TO_T = {m_dot * equipment["evaporation_time_s"] * KG_TO_T} т')
        if DEBUG:
            print(f'm_dot = {m_dot} кг/с')
            print(
                f'm_dot * equipment["evaporation_time_s"] * KG_TO_T = {m_dot * equipment["evaporation_time_s"] * KG_TO_T} т')

        # Проверяем не испарилось ли больше чем вылилось
        if m_dot * equipment["evaporation_time_s"] * KG_TO_T > result["ov_in_accident_t"]:
            result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
        else:
            result["ov_in_hazard_factor_t"] = m_dot * equipment["evaporation_time_s"] * MASS_IN_CLOUDE * KG_TO_T

    if scenario["scenario_line"] in (4, 6,):  # факельное горение газа/жидкости
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]

    if scenario["scenario_line"] in (7,):  # вспышка
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"] * MASS_IN_CLOUDE

    if scenario["scenario_line"] in (3, 5, 8):  # ликвидация
        result["ov_in_hazard_factor_t"] = 0

    if scenario["scenario_line"] in (9,):  # огненный шар
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"] * MASS_IN_BLEVE

    # print(f'result["ov_in_hazard_factor_t"] = {result["ov_in_hazard_factor_t"]}')
    # print(20 * "-")
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

    if scenario["scenario_line"] in (1,):  # пролив полная
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

        # print(zone)
        # print(20 * "-")
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

        # print(zone)
        # print(20 * "-")
        if DEBUG:
            print(zone)
            print(20 * "-")

    # -------------------------------------------------------------------------
    # Зоны поражения
    # -------------------------------------------------------------------------
    result["l_f"] = None
    result["d_f"] = None

    if scenario["scenario_line"] in (4, 6):  # факел жидкость
        type_jet = 2 if scenario["scenario_line"] == 4 else 0
        flow = liquid_flow if scenario["scenario_line"] == 4 else gas_flow
        zone = Torch().jetfire_size(flow, type_jet)

        result["l_f"] = zone[0]
        result["d_f"] = zone[1]

        # print(zone)
        # print(20 * "-")
        if DEBUG:
            print(zone)
            print(20 * "-")

    result["r_nkpr"] = None
    result["r_vsp"] = None

    if scenario["scenario_line"] in (7,):  # вспышка
        mass = result["ov_in_hazard_factor_t"]
        lower_concentration = float(explosion["lel_percent"])

        zone = LCLP().lower_concentration_limit(mass, mol_mass, t_boiling, lower_concentration)

        result["r_nkpr"] = int(zone[0])
        result["r_vsp"] = int(zone[1])

        # print(zone)
        # print(20 * "-")
        if DEBUG:
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

    if scenario["scenario_line"] in (9,):  # шар
        zone = Fireball().termal_class_zone(result["ov_in_hazard_factor_t"]*T_TO_KG, EF)
        result["q_600"] = int(zone[0])
        result["q_320"] = int(zone[1])
        result["q_220"] = int(zone[2])
        result["q_120"] = int(zone[3])

        # print(zone)
        # print(20 * "-")
        if DEBUG:
            print(zone)
            print(20 * "-")

    result["s_t"] = None

    # -------------------------------------------------------------------------
    # Последствия
    # -------------------------------------------------------------------------
    result["fatalities_count"] = None
    result["injured_count"] = None

    if scenario["scenario_line"] in (1,):  # пожар
        result["fatalities_count"] = max(0, equipment["possible_dead"] - 1)
        result["injured_count"] = max(0, equipment["possible_injured"] - 1)
    elif scenario["scenario_line"] in (2,):  # взрыв
        result["fatalities_count"] = equipment["possible_dead"]
        result["injured_count"] = equipment["possible_injured"]
    elif scenario["scenario_line"] in (3, 5, 8):  # ликвидация
        result["fatalities_count"] = 0
        result["injured_count"] = 0
    elif scenario["scenario_line"] in (4, 6, 7):  # факел, вспышка и пожар частичный
        result["fatalities_count"] = 0
        result["injured_count"] = 1
    elif scenario["scenario_line"] in (9, ):  # шар после нагрева
        result["fatalities_count"] = 0
        result["injured_count"] = 1
    #
    if DEBUG:
        print("Погибшие/раненые", result["fatalities_count"], result["injured_count"])
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Ущерб
    # -------------------------------------------------------------------------
    result["direct_losses"] = None
    result["liquidation_costs"] = None
    result["social_losses"] = None
    result["indirect_damage"] = None
    result["total_environmental_damage"] = None
    result["total_damage"] = None

    sc_line = int(scenario.get("scenario_line", 0))

    if 1 <= sc_line <= 9:
        k = DAMAGE_NINE_SC[sc_line - 1]
    else:
        # если прилетело неизвестное значение, безопасно считаем 0 ущерба по массе
        k = 0.0

    amount_t = float(result.get("amount_t", 0.0))
    mass_for_damage = k * amount_t

    base_damage = damage(
        mass_for_damage,
        int(result.get("fatalities_count", 0)),
        int(result.get("injured_count", 0)),
    )

    result["direct_losses"] = base_damage["direct_losses"]
    result["liquidation_costs"] = base_damage["liquidation_costs"]
    result["social_losses"] = base_damage["social_losses"]
    result["indirect_damage"] = base_damage["indirect_damage"]
    result["total_environmental_damage"] = base_damage["total_environmental_damage"]
    result["total_damage"] = base_damage["total_damage"]

    if DEBUG:
        print('Ущерб, тыс.руб', result["direct_losses"], result["social_losses"], result["total_environmental_damage"],
              result["total_damage"])
        print(20 * "-")
    # -------------------------------------------------------------------------
    # Риски
    # -------------------------------------------------------------------------
    result["collective_risk_fatalities"] = result["fatalities_count"] * result["scenario_frequency"]
    result["collective_risk_injured"] = result["injured_count"] * result["scenario_frequency"]
    result["expected_value"] = result["total_damage"] * result["scenario_frequency"]

    result["individual_risk_fatalities"] = result["collective_risk_fatalities"] / PEOPLE_COUNT
    result["individual_risk_injured"] = result["collective_risk_injured"] / PEOPLE_COUNT

    return result
