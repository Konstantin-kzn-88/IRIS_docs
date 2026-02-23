import sqlite3

from calculations.app._liguid_evaporation import (
    saturated_vapor_pressure_pa,
    evaporation_intensity_kg_m2_s,
)
from calculations.app._scenario_common import parse_substance_props
from core.config import KG_TO_T, P0, Pa_TO_kPa

# Включение/отключение отладочного вывода
DEBUG = False


def calculate_evaporation(substance: sqlite3.Row,
                          equipment: sqlite3.Row,
                          spill: float,
                          ov_in_accident_t: float):
    """
    Возвращает массу, участвующую в поражающем факторе
    (испарившуюся массу), в ТОННАХ.
    """

    props = parse_substance_props(substance)

    Pn = saturated_vapor_pressure_pa(
        equipment["substance_temperature_c"],
        props.t_boiling,
        props.evaporation_heat_J_per_kg,
        props.mol_mass,
        P0,
    )
    if DEBUG:
        print(f"Pn = {Pn * Pa_TO_kPa} кПа")

    W = evaporation_intensity_kg_m2_s(Pn, props.mol_mass, eta=1.0)
    m_dot = W * spill  # кг/с

    if DEBUG:
        print(f"m_dot = {m_dot} кг/с")
        print(m_dot * equipment["evaporation_time_s"] * KG_TO_T, "т испарилось")

    evaporated_t = m_dot * equipment["evaporation_time_s"] * KG_TO_T

    # Если испарилось больше, чем вылилось → участвует только масса аварии
    if evaporated_t > ov_in_accident_t:
        return ov_in_accident_t

    # Иначе возвращаем массу испарившегося
    return evaporated_t