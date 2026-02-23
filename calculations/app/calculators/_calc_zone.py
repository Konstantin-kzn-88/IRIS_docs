import sqlite3

from calculations.app._lower_concentration import LCLP
from calculations.app._scenario_common import parse_substance_props
from calculations.app._strait_fire import Strait_fire
from calculations.app._tvs_explosion import Explosion
from core.config import MSG, WIND, T_TO_KG

# Включение/отключение отладочного вывода
DEBUG = False  # True -> печатаем отладку, False -> молчим



def calculate_zone(
    substance: sqlite3.Row,
    equipment: sqlite3.Row,
    spill: float,
    calc_code: int,
    ov_in_hazard_factor_t: float = 0.0,
):
    """
    "calc_code_mapping": {
      "0": "ликвидация аварии",
      "1": "пожар пролива",
      "2": "взрыв облака",
      "3": "пожар вспышка",
      "4": "токсическое поражение",
      "5": "факельное горение",
      "6": "огненный шар",
      "7": "химически опасный пролив"
    }

    На входе:
        substance  – строка вещества из БД
        equipment  – строка оборудования из БД
        spill      – площадь пролива, м2
        calc_code  – тип сценария по typical_scenarios.json
        ov_in_hazard_factor_t – масса, участвующая в поражающем факторе, т
                                 (нужна для взрыва и вспышки)

    На выходе:
        dict с ключами:
        q_*, p_*, l_f, d_f, r_*, l_pt, p_pt, q_600..q_120, s_t
    """

    result = {}

    # -------------------------------------------------------------------------
    # Пожар пролива
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
    # -------------------------------------------------------------------------
    # Факел
    # -------------------------------------------------------------------------
    result["l_f"] = None
    result["d_f"] = None
    # -------------------------------------------------------------------------
    # НКПР / вспышка
    # -------------------------------------------------------------------------
    result["r_nkpr"] = None
    result["r_vsp"] = None
    # -------------------------------------------------------------------------
    # Токсическое воздействие
    # -------------------------------------------------------------------------
    result["l_pt"] = None
    result["p_pt"] = None
    # -------------------------------------------------------------------------
    # Огненный шар / тепловые дозы
    # -------------------------------------------------------------------------
    result["q_600"] = None
    result["q_320"] = None
    result["q_220"] = None
    result["q_120"] = None
    # -------------------------------------------------------------------------
    # Токсичный пролив
    # -------------------------------------------------------------------------
    result["s_t"] = None

    # -------------------------------------------------------------------------
    # Свойства вещества
    # -------------------------------------------------------------------------
    props = parse_substance_props(substance)
    explosion = props.explosion
    mol_mass = props.mol_mass
    t_boiling = props.t_boiling

    # -------------------------------------------------------------------------
    # Расчёт по calc_code
    # -------------------------------------------------------------------------

    # 0 – ликвидация аварии: просто возвращаем пустые зоны
    if calc_code == 0:
        return result

    # 1 – пожар пролива
    if calc_code == 1:
        zone = Strait_fire().termal_class_zone(
            S_spill=spill,
            m_sg=MSG,
            mol_mass=mol_mass,
            t_boiling=t_boiling,
            wind_velocity=WIND,
        )
        result["q_10_5"], result["q_7_0"], result["q_4_2"], result["q_1_4"] = map(int, zone)

        if DEBUG:
            print("POOL FIRE ZONES:", zone)

        return result

    # 2 – взрыв облака ТВС
    elif calc_code == 2:
        zone = Explosion().explosion_class_zone(
            int(explosion["explosion_hazard_class"]),
            equipment["clutter_degree"],
            ov_in_hazard_factor_t * T_TO_KG,
            int(explosion["heat_of_combustion_kJ_per_kg"]),
            int(explosion["expansion_degree"]),
            int(explosion["energy_reserve_factor"]),
        )
        # zone[0] – класс, дальше радиусы
        result["p_70"], result["p_28"], result["p_14"], result["p_5"], result["p_2"] = map(int, zone[1:6])

        if DEBUG:
            print("EXPLOSION ZONES:", zone)

        return result

    # 3 – пожар-вспышка
    elif calc_code == 3:
        zone = LCLP().lower_concentration_limit(
            ov_in_hazard_factor_t,
            mol_mass,
            t_boiling,
            float(explosion["lel_percent"]),
        )
        result["r_nkpr"], result["r_vsp"] = map(int, zone)

        if DEBUG:
            print("FLASH FIRE ZONES:", zone)

        return result

    # 4–7 – токсика, факел, огненный шар, токсичный пролив – пока заглушки
    else:
        return result