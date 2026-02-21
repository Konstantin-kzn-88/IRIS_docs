import sqlite3

from calculations.app._liguid_evaporation import evaporation_intensity_kg_m2_s, saturated_vapor_pressure_pa
from calculations.app._lower_concentration import LCLP
from calculations.app._strait_fire import Strait_fire
from calculations.app._tvs_explosion import Explosion
from calculations.app._base_damage_state import damage

from calculations.app._scenario_common import (
    init_result_base,
    parse_substance_props,
    calc_spill_area_m2,
    apply_damage_block,
    apply_risk_block,
)

from core.config import (
    KG_TO_T,
    MASS_IN_CLOUDE,
    MASS_TO_PART,
    MSG,
    WIND,
    SPILL_TO_PART,
    T_TO_KG,
    Pa_TO_kPa,
    P0,
    DAMAGE_SIX_SC,
)

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

    if DEBUG:
        print("Считаем сценарий:", scenario_no, equipment["equipment_name"])

    # -------------------------------------------------------------------------
    # Обязательные поля + частоты
    # -------------------------------------------------------------------------
    result = init_result_base(equipment, scenario, scenario_no)

    # -------------------------------------------------------------------------
    # Свойства вещества
    # -------------------------------------------------------------------------
    props = parse_substance_props(substance)
    physical = props.physical
    explosion = props.explosion

    density_liquid = props.density_liquid
    density_gas = props.density_gas
    mol_mass = props.mol_mass
    t_boiling = props.t_boiling
    evaporation_heat_J_per_kg = props.evaporation_heat_J_per_kg

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

    sc_line = int(scenario.get("scenario_line", 0))

    if sc_line in (1, 2, 3):
        result["ov_in_accident_t"] = result["amount_t"]

    if sc_line in (4, 5, 6):
        result["ov_in_accident_t"] = result["amount_t"] * MASS_TO_PART

    if DEBUG:
        print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')

    if sc_line in (1, 4):
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]

    # -------------------------------------------------------------------------
    # Пролив и испарение
    # -------------------------------------------------------------------------
    spill = calc_spill_area_m2(
        float(result["ov_in_accident_t"]),
        equipment,
        is_full_spill=(sc_line in (1, 2, 3)),
        spill_to_part=SPILL_TO_PART,
    )

    if DEBUG:
        print(f"spill={spill} м2")

    if sc_line in (2, 5):
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
            print(m_dot * equipment["evaporation_time_s"] * KG_TO_T, "т испарилось")

        if m_dot * equipment["evaporation_time_s"] * KG_TO_T > result["ov_in_accident_t"]:
            result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
        else:
            result["ov_in_hazard_factor_t"] = (
                m_dot * equipment["evaporation_time_s"] * MASS_IN_CLOUDE * KG_TO_T
            )

    if sc_line in (3, 6):
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

    if sc_line in (1, 4):
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

    if sc_line in (2,):
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

    if sc_line in (5,):
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
    result["fatalities_count"] = None
    result["injured_count"] = None

    if sc_line in (1,):
        result["fatalities_count"] = max(0, equipment["possible_dead"] - 1)
        result["injured_count"] = max(0, equipment["possible_injured"] - 1)
    elif sc_line in (2,):
        result["fatalities_count"] = equipment["possible_dead"]
        result["injured_count"] = equipment["possible_injured"]
    elif sc_line in (3, 6):
        result["fatalities_count"] = 0
        result["injured_count"] = 0
    elif sc_line in (4, 5):  # вспышка и пожар частичный
        result["fatalities_count"] = 0
        result["injured_count"] = 1

    if DEBUG:
        print("Погибшие/раненые", result["fatalities_count"], result["injured_count"])
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Ущерб
    # -------------------------------------------------------------------------
    apply_damage_block(
        result,
        scenario,
        damage_coeffs=DAMAGE_SIX_SC,
        damage_func=damage,
    )

    if DEBUG:
        print(
            "Ущерб, тыс.руб",
            result["direct_losses"],
            result["social_losses"],
            result["total_environmental_damage"],
            result["total_damage"],
        )
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Риски
    # -------------------------------------------------------------------------
    apply_risk_block(result)

    return result