import sqlite3

from calculations.app._jet_fire import Torch
from calculations.app._liguid_evaporation import evaporation_intensity_kg_m2_s, saturated_vapor_pressure_pa
from calculations.app._liquid_flow import liquid_leak_mass_flow
from calculations.app._lower_concentration import LCLP
from calculations.app._strait_fire import Strait_fire
from calculations.app._base_damage_line import damage
from calculations.app._tvs_explosion import Explosion

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
    MSG,
    WIND,
    SPILL_TO_PART,
    Pa_TO_kPa,
    P0,
    D_MM_JET_LIQUID,
    DAMAGE_SIX_SC,
    T_TO_KG,
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
    explosion = props.explosion

    density = props.density_liquid
    mol_mass = props.mol_mass
    t_boiling = props.t_boiling
    evaporation_heat_J_per_kg = props.evaporation_heat_J_per_kg

    sc_line = int(scenario.get("scenario_line", 0))

    # -------------------------------------------------------------------------
    # Количество ОВ
    # -------------------------------------------------------------------------
    volume = equipment["volume_m3"]
    result["amount_t"] = volume * density * KG_TO_T

    if DEBUG:
        print(f'result["amount_t"] = {result["amount_t"]}')

    flow = liquid_leak_mass_flow(
        equipment["pressure_mpa"],
        D_MM_JET_LIQUID,
        density,
    )

    # -------------------------------------------------------------------------
    # Масса в аварии / в ПФ
    # -------------------------------------------------------------------------
    if sc_line in (1, 2, 3, 4, 5, 6):  # пролив
        result["ov_in_accident_t"] = result["amount_t"] + flow * equipment["shutdown_time_s"] * KG_TO_T

    if sc_line in (1, 2, 4):  # пролив или факел
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]

    # -------------------------------------------------------------------------
    # Пролив и испарение
    #   В исходнике: "полный пролив" только для scenario_line == 5,
    #   иначе пролив = spill_area_m2 * SPILL_TO_PART (если spill_area_m2 != 0).
    # -------------------------------------------------------------------------
    spill = calc_spill_area_m2(
        float(result["ov_in_accident_t"]),
        equipment,
        is_full_spill=(sc_line in (5,)),
        spill_to_part=SPILL_TO_PART,
    )

    if DEBUG:
        print(f"spill={spill} м2")

    if sc_line in (5,):  # испарение для вспышки/взрыва (по исходнику)
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
        m_dot = W * spill  # кг/с

        if DEBUG:
            print(f"m_dot = {m_dot} кг/с")
            print(
                f'm_dot * equipment["evaporation_time_s"] * KG_TO_T = '
                f'{m_dot * equipment["evaporation_time_s"] * KG_TO_T} т'
            )

        if m_dot * equipment["evaporation_time_s"] * KG_TO_T > result["ov_in_accident_t"]:
            result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
        else:
            result["ov_in_hazard_factor_t"] = (
                m_dot * equipment["evaporation_time_s"] * MASS_IN_CLOUDE * KG_TO_T
            )

    if sc_line in (3, 6):  # ликвидация
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

    if sc_line in (2, 4):
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
    # Избыточное давление (взрыв)
    # -------------------------------------------------------------------------
    result["p_70"] = None
    result["p_28"] = None
    result["p_14"] = None
    result["p_5"] = None
    result["p_2"] = None

    if sc_line in (5,):
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
    result["l_f"] = None
    result["d_f"] = None

    if sc_line in (1,):  # факел жидкость
        type_jet = 2
        zone = Torch().jetfire_size(flow, type_jet)
        result["l_f"], result["d_f"] = zone

        if DEBUG:
            print(zone)
            print(20 * "-")

    result["r_nkpr"] = None
    result["r_vsp"] = None

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
    # Последствия (как в исходнике)
    # -------------------------------------------------------------------------
    result["fatalities_count"] = None
    result["injured_count"] = None

    if sc_line in (1, 4):
        result["fatalities_count"] = 1
        result["injured_count"] = 1
    elif sc_line in (2,):
        result["fatalities_count"] = max(0, equipment["possible_dead"] - 3)
        result["injured_count"] = max(0, equipment["possible_injured"] - 4)
    elif sc_line in (5,):
        result["fatalities_count"] = max(0, equipment["possible_dead"] - 2)
        result["injured_count"] = max(0, equipment["possible_injured"] - 3)
    elif sc_line in (3, 6):
        result["fatalities_count"] = 0
        result["injured_count"] = 0

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

    # -------------------------------------------------------------------------
    # Риски
    # -------------------------------------------------------------------------
    apply_risk_block(result)

    return result