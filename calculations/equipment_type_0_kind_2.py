import sqlite3

from calculations.app._jet_fire import Torch
from calculations.app._gas_flow import gas_leak_mass_flow
from calculations.app._lower_concentration import LCLP
from calculations.app._base_damage_line import damage
from calculations.app._pipeline_volume_m3 import pipeline_internal_volume_m3
from calculations.app._tvs_explosion import Explosion

from calculations.app._scenario_common import (
    init_result_base,
    parse_substance_props,
    apply_damage_block,
    apply_risk_block,
)

from core.config import (
    KG_TO_T,
    MASS_IN_CLOUDE,
    D_MM_JET_GAS,
    MASS_TO_PART,
    T_TO_KG,
    DAMAGE_EIGHT_SC,
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
    # Физические свойства / взрывопожарные свойства
    # -------------------------------------------------------------------------
    props = parse_substance_props(substance)
    physical = props.physical
    explosion = props.explosion

    density_gas = props.density_gas
    mol_mass = props.mol_mass
    t_boiling = props.t_boiling
    substance_temperature_c = float(equipment["substance_temperature_c"])

    # -------------------------------------------------------------------------
    # Количество ОВ
    # -------------------------------------------------------------------------
    pipeline_volume = pipeline_internal_volume_m3(
        equipment["length_m"],
        equipment["diameter_mm"],
        equipment["wall_thickness_mm"],
    )
    result["amount_t"] = pipeline_volume * density_gas * KG_TO_T

    if DEBUG:
        print(f'result["amount_t"] = {result["amount_t"]}')

    flow = gas_leak_mass_flow(
        equipment["pressure_mpa"],
        D_MM_JET_GAS,
        substance_temperature_c,
        mol_mass,
    )
    flow_part = flow * MASS_TO_PART

    sc_line = int(scenario.get("scenario_line", 0))

    if sc_line in (1, 2, 3, 4):  # полная
        result["ov_in_accident_t"] = result["amount_t"] + flow * equipment["shutdown_time_s"] * KG_TO_T

    if sc_line in (5, 6, 7, 8):  # частичная
        result["ov_in_accident_t"] = result["amount_t"] + flow_part * equipment["shutdown_time_s"] * KG_TO_T

    # -------------------------------------------------------------------------
    # Масса, участвующая в ПФ
    # -------------------------------------------------------------------------
    if sc_line in (1, 3, 5, 7):          # факел и вспышка
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
    elif sc_line in (2, 6):              # взрыв
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"] * MASS_IN_CLOUDE
    elif sc_line in (4, 8):              # ликвидация
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"] * MASS_IN_CLOUDE

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

    # -------------------------------------------------------------------------
    # Избыточное давление
    # -------------------------------------------------------------------------
    result["p_70"] = None
    result["p_28"] = None
    result["p_14"] = None
    result["p_5"] = None
    result["p_2"] = None

    if sc_line in (2, 6):
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

    if sc_line in (1,):  # факел газ (полная)
        type_jet = 0
        zone = Torch().jetfire_size(flow, type_jet)
        result["l_f"] = zone[0]
        result["d_f"] = zone[1]

        if DEBUG:
            print(zone)
            print(20 * "-")

    elif sc_line in (5,):  # факел газ (частичная)
        type_jet = 0
        zone = Torch().jetfire_size(flow_part, type_jet)
        result["l_f"] = zone[0]
        result["d_f"] = zone[1]

        if DEBUG:
            print(zone)
            print(20 * "-")

    result["r_nkpr"] = None
    result["r_vsp"] = None

    if sc_line in (3, 7):  # вспышка
        mass = result["ov_in_hazard_factor_t"]
        lower_concentration = float(explosion["lel_percent"])

        zone = LCLP().lower_concentration_limit(mass, mol_mass, t_boiling, lower_concentration)

        result["r_nkpr"] = int(zone[0])
        result["r_vsp"] = int(zone[1])

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
    result["s_t"] = None

    # -------------------------------------------------------------------------
    # Последствия
    # -------------------------------------------------------------------------
    result["fatalities_count"] = None
    result["injured_count"] = None

    if sc_line in (1,):  # с ПФ
        result["fatalities_count"] = max(0, equipment["possible_dead"] - 1)
        result["injured_count"] = max(0, equipment["possible_injured"] - 1)
    elif sc_line in (2,):  # с ПФ
        result["fatalities_count"] = max(0, equipment["possible_dead"])
        result["injured_count"] = max(0, equipment["possible_injured"])
    elif sc_line in (3, 5, 6, 7):  # с ПФ
        result["fatalities_count"] = 1
        result["injured_count"] = 1
    elif sc_line in (4, 8):
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
        damage_coeffs=DAMAGE_EIGHT_SC,
        damage_func=damage,
    )

    # -------------------------------------------------------------------------
    # Риски
    # -------------------------------------------------------------------------
    apply_risk_block(result)

    return result