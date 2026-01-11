import sqlite3


def get_used_substances(conn) -> list[dict]:
    sql = """
    SELECT DISTINCT s.*
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    JOIN substances s ON s.id = e.substance_id
    ORDER BY s.name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_used_equipment(conn) -> list[dict]:
    sql = """
    SELECT DISTINCT e.*
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_hazard_distribution(conn) -> list[dict]:
    """
    Распределение опасного вещества по оборудованию:
    1) Наименование оборудования (только то, что есть в calculations)
    2) Наименование вещества
    3) Количество опасного вещества (amount_t из calculations)
       Если по одному оборудованию несколько строк calculations, берём MAX(amount_t)
       (обычно amount_t одинаков для сценариев одного оборудования).
    4) phase_state (equipment)
    5) pressure_mpa (equipment)
    6) substance_temperature_c (equipment)
    """
    sql = """
    SELECT
        e.id AS equipment_id,
        e.equipment_name AS equipment_name,
        s.name AS substance_name,
        MAX(c.amount_t) AS amount_t,
        e.phase_state AS phase_state,
        e.pressure_mpa AS pressure_mpa,
        e.substance_temperature_c AS substance_temperature_c
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    JOIN substances s ON s.id = e.substance_id
    GROUP BY e.id, e.equipment_name, s.name, e.phase_state, e.pressure_mpa, e.substance_temperature_c
    ORDER BY e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_scenarios(conn) -> list[dict]:
    sql = """
    SELECT
        c.scenario_no,
        c.base_frequency,
        c.accident_event_probability,
        c.scenario_frequency,

        e.equipment_name,
        e.equipment_type,

        s.kind AS substance_kind
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    JOIN substances s ON s.id = e.substance_id
    ORDER BY e.equipment_name, e.equipment_type, s.kind, c.scenario_no
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_ov_amounts_in_accident(conn) -> list[dict]:
    """
    Оценка количества опасного вещества в аварии (по таблице calculations).

    Возвращает строки с полями:
      - equipment_name
      - scenario_no
      - ov_in_accident_t
      - ov_in_hazard_factor_t
    """
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.ov_in_accident_t AS ov_in_accident_t,
        c.ov_in_hazard_factor_t AS ov_in_hazard_factor_t
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY c.scenario_no, e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_impact_zones(conn) -> list[dict]:
    sql = """
    SELECT
        e.equipment_name,
        c.scenario_no,

        c.q_10_5,
        c.q_7_0,
        c.q_4_2,
        c.q_1_4,

        c.p_70,
        c.p_28,
        c.p_14,
        c.p_5,
        c.p_2,

        c.l_f,
        c.d_f,
        c.r_nkpr,
        c.r_vsp,
        c.l_pt,
        c.p_pt,

        c.q_600,
        c.q_320,
        c.q_220,
        c.q_120,

        c.s_t
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY e.equipment_name, c.scenario_no
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_personnel_casualties(conn) -> list[dict]:
    """Оценка количества погибших/пострадавших (по таблице calculations).

    Возвращает строки с полями:
      - equipment_name
      - scenario_no
      - fatalities_count
      - injured_count
    """
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.fatalities_count AS fatalities_count,
        c.injured_count AS injured_count
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY c.scenario_no, e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_damage(conn) -> list[dict]:
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,

        c.direct_losses AS direct_losses,
        c.liquidation_costs AS liquidation_costs,
        c.social_losses AS social_losses,
        c.indirect_damage AS indirect_damage,
        c.total_environmental_damage AS total_environmental_damage,
        c.total_damage AS total_damage
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY c.scenario_no, e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_collective_risk(conn) -> list[dict]:
    sql = """
    SELECT
        e.hazard_component AS hazard_component,
        SUM(c.collective_risk_fatalities) AS collective_risk_fatalities,
        SUM(c.collective_risk_injured) AS collective_risk_injured
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    GROUP BY e.hazard_component
    ORDER BY e.hazard_component
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def get_individual_risk(conn) -> list[dict]:
    sql = """
    SELECT
        e.hazard_component AS hazard_component,
        SUM(c.individual_risk_fatalities) AS individual_risk_fatalities,
        SUM(c.individual_risk_injured) AS individual_risk_injured
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    GROUP BY e.hazard_component
    ORDER BY e.hazard_component
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def get_fatal_accident_frequency_range(conn):
    """
    Возвращает (min_freq, max_freq) для сценариев с >= 1 погибшим.
    Если таких сценариев нет — возвращает (None, None).
    """
    sql = """
    SELECT
        MIN(c.scenario_frequency) AS min_freq,
        MAX(c.scenario_frequency) AS max_freq
    FROM calculations c
    WHERE c.fatalities_count >= 1
    """
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if row is None:
        return None, None
    return row[0], row[1]


def get_max_damage_by_hazard_component(conn) -> list[dict]:
    sql = """
    SELECT
        e.hazard_component AS hazard_component,
        MAX(c.total_damage) AS max_total_damage,
        MAX(c.total_environmental_damage) AS max_total_environmental_damage
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    GROUP BY e.hazard_component
    ORDER BY e.hazard_component
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]



def get_fn_source_rows(conn) -> list[dict]:
    """
    Источник для F/N: (fatalities_count, scenario_frequency) по всем сценариям.
    Берём только записи, где fatalities_count не NULL и scenario_frequency не NULL.
    """
    sql = """
    SELECT
        c.fatalities_count AS fatalities_count,
        c.scenario_frequency AS scenario_frequency
    FROM calculations c
    WHERE c.fatalities_count IS NOT NULL
      AND c.scenario_frequency IS NOT NULL
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_fg_source_rows(conn) -> list[dict]:
    """
    Источник для F/G: (total_damage, scenario_frequency) по всем сценариям.
    total_damage ожидается в тыс.руб (как в расчётах); далее в графике переводим в млн.руб.
    Берём только записи, где total_damage и scenario_frequency не NULL.
    """
    sql = """
    SELECT
        c.total_damage AS total_damage,
        c.scenario_frequency AS scenario_frequency
    FROM calculations c
    WHERE c.total_damage IS NOT NULL
      AND c.scenario_frequency IS NOT NULL
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_pareto_risk_source_rows(conn) -> list[dict]:
    """
    Источник для Pareto по риску (сценарии/оборудование).
    Возвращает строки по каждому (equipment, scenario_no) с рассчитанными в calculations показателями риска.
    """
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.collective_risk_fatalities AS collective_risk_fatalities,
        c.collective_risk_injured AS collective_risk_injured
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    ORDER BY c.scenario_no, e.equipment_name
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_pareto_damage_source_rows(conn) -> list[dict]:
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.total_damage AS total_damage
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    WHERE c.total_damage IS NOT NULL
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_pareto_environmental_damage_source_rows(conn):
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.total_environmental_damage AS total_environmental_damage
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    WHERE c.total_environmental_damage IS NOT NULL
          AND c.total_environmental_damage > 0
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_max_losses_by_hazard_component(conn) -> list[dict]:
    sql = """
    SELECT
        e.hazard_component AS hazard_component,
        MAX(c.direct_losses) AS max_direct_losses,
        MAX(c.total_environmental_damage) AS max_total_environmental_damage
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    GROUP BY e.hazard_component
    ORDER BY e.hazard_component
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_risk_matrix_rows(conn) -> list[dict]:
    sql = """
    SELECT
        e.equipment_name AS equipment_name,
        c.scenario_no AS scenario_no,
        c.scenario_frequency AS scenario_frequency,
        c.fatalities_count AS fatalities_count
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    WHERE c.scenario_frequency IS NOT NULL
      AND c.fatalities_count IS NOT NULL
      AND c.fatalities_count >= 1
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_risk_matrix_damage_rows(conn) -> list[dict]:
    sql = """
    SELECT
        c.scenario_no AS scenario_no,
        c.scenario_frequency AS scenario_frequency,
        c.total_damage AS total_damage
    FROM calculations c
    WHERE c.scenario_frequency IS NOT NULL
      AND c.total_damage IS NOT NULL
      AND c.total_damage > 0
      AND c.scenario_frequency > 0
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def open_db(db_path):
    return sqlite3.connect(db_path)
