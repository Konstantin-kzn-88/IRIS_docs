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


def open_db(db_path):
    return sqlite3.connect(db_path)
