import sqlite3

from calculations.app._base_damage_line import damage

from calculations.app.calculators._calc_amount import calculate_amount
from calculations.app.calculators._calc_damage import calculate_damage
from calculations.app.calculators._calc_people import calculate_people_damage
from calculations.app.calculators._calc_risk import calculate_risk
from calculations.app.calculators._calc_spill_area import calc_spill_area_m2
from calculations.app.calculators._calc_evaporation_mass import calculate_evaporation
from calculations.app.calculators._calc_zone import calculate_zone
from calculations.app.scenario.scenario_matrix import get_calc_code
from calculations.app.calculators._calc_base_result import init_result_base

from core.config import (
    MASS_IN_CLOUDE,
    MASS_TO_PART,
    SPILL_TO_PART,
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

    # Номер ветки сценария
    sc_line = int(scenario.get("scenario_line", 0))
    # Полные и частичные варианты
    FULL_SCENARIO_LINE = (1, 2, 3)
    PART_SCENARIO_LINE = (4, 5, 6)
    # -------------------------------------------------------------------------
    # Обязательные поля + частоты
    # -------------------------------------------------------------------------
    result = init_result_base(equipment, scenario, scenario_no)
    # -------------------------------------------------------------------------
    # Количество ОВ (через общий калькулятор)
    # -------------------------------------------------------------------------
    amount_info = calculate_amount(
        equipment_type=equipment["equipment_type"],
        kind=0,  # ЛВЖ для этого файла
        equipment=equipment,
        substance=substance
    )

    if DEBUG:
        print("amount_info:", amount_info)

    # базовая масса в оборудовании
    result["amount_t"] = amount_info["amount_t"]
    # базовая масса, которая «может выйти» (полный пролив)
    base_ov_in_accident_t = amount_info["ov_in_accident_t"]
    # учитываем ПОЛНЫЙ / ЧАСТИЧНЫЙ на уровне сценария
    if sc_line in FULL_SCENARIO_LINE:  # полностью
        result["ov_in_accident_t"] = base_ov_in_accident_t
    elif sc_line in PART_SCENARIO_LINE:  # частичная разгерметизация
        result["ov_in_accident_t"] = base_ov_in_accident_t * MASS_TO_PART
    else:
        result["ov_in_accident_t"] = 0.0

    if DEBUG:
        print(f'result["ov_in_accident_t"] = {result["ov_in_accident_t"]}')

    # -------------------------------------------------------------------------
    # Прогнозирование пролива опасного вещеества
    # -------------------------------------------------------------------------
    spill = calc_spill_area_m2(
        float(result["ov_in_accident_t"]),
        equipment,
        is_full_spill=(sc_line in FULL_SCENARIO_LINE),
        spill_to_part=SPILL_TO_PART,
    )
    if DEBUG:
        print(f"spill={spill} м2")

    # -------------------------------------------------------------------------
    # Испарение (т.к. ЛВЖ испаряются)
    # -------------------------------------------------------------------------
    evaporation = calculate_evaporation(
        substance=substance,
        equipment=equipment,
        spill=spill,
        ov_in_accident_t=result["ov_in_accident_t"],
    )
    # -------------------------------------------------------------------------
    # Количество опасного вещества в поражающем факторе
    # -------------------------------------------------------------------------
    if sc_line in (1, 4):  # пролив полная/частичная
        result["ov_in_hazard_factor_t"] = result["ov_in_accident_t"]
    elif sc_line in (2,):  # взрыв
        result["ov_in_hazard_factor_t"] = evaporation * MASS_IN_CLOUDE
    elif sc_line in (5,):  # вспышка
        result["ov_in_hazard_factor_t"] = evaporation
    elif sc_line in (3, 6):  # ликвидация
        result["ov_in_hazard_factor_t"] = 0

    if DEBUG:
        print(f'result["ov_in_hazard_factor_t"] = {result["ov_in_hazard_factor_t"]}')
        print(20 * "-")

    # -------------------------------------------------------------------------
    # Определение расчетного кода (calc_code, см. typical_scenarios.json)
    # -------------------------------------------------------------------------
    calc_code = get_calc_code(equipment["equipment_type"], substance['kind'], sc_line)
    if DEBUG:
        print(f'calc_code = {calc_code}')
        print(20 * "-")
    # -------------------------------------------------------------------------
    # Расчеты
    # -------------------------------------------------------------------------
    zones = calculate_zone(substance, equipment, spill, calc_code, result["ov_in_hazard_factor_t"])
    result.update(zones)
    # -------------------------------------------------------------------------
    # Последствия
    # -------------------------------------------------------------------------
    people = calculate_people_damage(
        sc_line=sc_line,
        equipment_type=equipment["equipment_type"],
        kind=substance["kind"],
        possible_dead=equipment["possible_dead"],
        possible_injured=equipment["possible_injured"],
    )
    result.update(people)
    # -------------------------------------------------------------------------
    # Ущерб
    # -------------------------------------------------------------------------
    damage_scenario = calculate_damage(scenario, damage_coeffs=DAMAGE_SIX_SC, damage_func=damage,
                                       ov_in_accident_t=result["ov_in_accident_t"])
    result.update(damage_scenario)
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
    calculate_risk(result)

    return result
