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
    ORDER BY e.id
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def get_scenarios(conn) -> list[dict]:
    sql = """
    SELECT
        e.id AS equipment_id,
        c.scenario_no,
        (ROW_NUMBER() OVER (PARTITION BY e.id ORDER BY c.scenario_no) - 1) AS scenario_idx,
        c.base_frequency,
        c.accident_event_probability,
        c.scenario_frequency,

        e.equipment_name,
        e.equipment_type,

        s.kind AS substance_kind
    FROM calculations c
    JOIN equipment e ON e.id = c.equipment_id
    JOIN substances s ON s.id = e.substance_id
    ORDER BY c.scenario_no, e.equipment_name
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
    ORDER BY c.scenario_no, e.equipment_name
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
    ORDER BY MIN(e.id)
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
    ORDER BY MIN(e.id)
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


def get_top_scenarios_by_hazard_component(conn) -> list[dict]:
    """
    Таблица наиболее опасных и наиболее вероятных сценариев аварии по составляющим объекта.

    Наиболее опасный:
      1) максимум fatalities_count
      2) при равенстве fatalities_count — максимум total_damage

    Наиболее вероятный:
      1) максимум scenario_frequency

    Возвращает список строк (по 2 строки на hazard_component):
      hazard_component, scenario_type, scenario_no, equipment_name, fatalities_count, total_damage, scenario_frequency
    """
    sql = """
    SELECT
        c.hazard_component,
        c.scenario_no,
        c.equipment_name,
        c.fatalities_count,
        c.total_damage,
        c.scenario_frequency
    FROM calculations c
    ORDER BY c.hazard_component
    """
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    best = {}  # hazard_component -> {"dangerous": row, "probable": row}

    for r in rows:
        comp = r.get("hazard_component")
        if comp is None:
            continue

        if comp not in best:
            best[comp] = {"dangerous": r, "probable": r}
            continue

        # most dangerous
        d = best[comp]["dangerous"]
        r_f = r.get("fatalities_count") or 0
        d_f = d.get("fatalities_count") or 0
        if r_f > d_f:
            best[comp]["dangerous"] = r
        elif r_f == d_f:
            r_dmg = r.get("total_damage") or 0
            d_dmg = d.get("total_damage") or 0
            if r_dmg > d_dmg:
                best[comp]["dangerous"] = r

        # most probable
        p = best[comp]["probable"]
        r_fr = r.get("scenario_frequency") or 0
        p_fr = p.get("scenario_frequency") or 0
        if r_fr > p_fr:
            best[comp]["probable"] = r

    out = []
    for comp in sorted(best.keys(), key=lambda x: str(x)):
        d = best[comp]["dangerous"]
        p = best[comp]["probable"]

        out.append({
            "hazard_component": comp,
            "scenario_type": "dangerous",
            "scenario_no": d.get("scenario_no"),
            "equipment_name": d.get("equipment_name"),
            "fatalities_count": d.get("fatalities_count"),
            "total_damage": d.get("total_damage"),
            "scenario_frequency": d.get("scenario_frequency"),
        })
        out.append({
            "hazard_component": comp,
            "scenario_type": "probable",
            "scenario_no": p.get("scenario_no"),
            "equipment_name": p.get("equipment_name"),
            "fatalities_count": p.get("fatalities_count"),
            "total_damage": p.get("total_damage"),
            "scenario_frequency": p.get("scenario_frequency"),
        })

    return out


def get_damage_by_component(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            hazard_component,
            MAX(total_damage) AS damage
        FROM calculations
        WHERE total_damage IS NOT NULL
        GROUP BY hazard_component
    """)
    return {row[0]: row[1] for row in cur.fetchall()}


def get_substances_by_component(conn):
    """
    Количество веществ по составляющим объекта.

    Берем amount_t из calculations, но чтобы не удваивать по сценариям:
    - агрегируем до уровня (hazard_component, equipment_id)
    - затем связываем equipment -> substances и суммируем по веществу
    """
    cur = conn.cursor()
    cur.execute("""
        WITH eq_amount AS (
            SELECT
                hazard_component,
                equipment_id,
                MAX(amount_t) AS amount_t
            FROM calculations
            GROUP BY hazard_component, equipment_id
        )
        SELECT
            ea.hazard_component,
            s.name AS substance_name,
            SUM(ea.amount_t) AS mass_t
        FROM eq_amount ea
        JOIN equipment e ON e.id = ea.equipment_id
        JOIN substances s ON s.id = e.substance_id
        GROUP BY ea.hazard_component, s.name
        ORDER BY ea.hazard_component, s.name
    """)

    result = {}
    for comp, substance_name, mass_t in cur.fetchall():  # tuples
        result.setdefault(comp, []).append((substance_name, mass_t))
    return result


def get_top_scenarios_by_hazard_component(conn) -> list[dict]:
    """
    Возвращает по каждой hazard_component две строки:
    - наиболее опасный (fatalities_count desc, tie -> total_damage desc)
    - наиболее вероятный (scenario_frequency desc)

    Поля:
    hazard_component, scenario_type, scenario_no, equipment_name,
    fatalities_count, total_damage, scenario_frequency
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.hazard_component,
            c.scenario_no,
            c.fatalities_count,
            c.total_damage,
            c.scenario_frequency,
            e.equipment_name
        FROM calculations c
        JOIN equipment e ON e.id = c.equipment_id
        WHERE c.hazard_component IS NOT NULL
    """)
    rows = cur.fetchall()

    best = {}  # comp -> {"dangerous": tuple, "probable": tuple}

    for comp, sc_no, fat, dmg, freq, eq_name in rows:
        item = {
            "hazard_component": comp,
            "scenario_no": sc_no,
            "equipment_name": eq_name,
            "fatalities_count": fat if fat is not None else 0,
            "total_damage": dmg if dmg is not None else 0,
            "scenario_frequency": freq if freq is not None else 0,
        }

        if comp not in best:
            best[comp] = {"dangerous": item, "probable": item}
            continue

        # наиболее опасный: fatalities desc, tie -> total_damage desc
        d = best[comp]["dangerous"]
        if (
                item["fatalities_count"] > d["fatalities_count"] or
                (item["fatalities_count"] == d["fatalities_count"] and item["total_damage"] > d["total_damage"])
        ):
            best[comp]["dangerous"] = item

        # наиболее вероятный: scenario_frequency desc
        p = best[comp]["probable"]
        if item["scenario_frequency"] > p["scenario_frequency"]:
            best[comp]["probable"] = item

    out = []
    for comp, vv in best.items():
        out.append({**vv["dangerous"], "scenario_type": "dangerous"})
        out.append({**vv["probable"], "scenario_type": "probable"})
    return out


def get_calculation_row_for_top_scenario(conn, hazard_component, scenario_no, equipment_name):
    """
    Возвращает одну (наиболее релевантную) строку calculations для заданного:
    - hazard_component
    - scenario_no
    - equipment_name

    Нужна для извлечения полей поражающих факторов (q_*, p_*, l_f, ...).
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.q_10_5, c.q_7_0, c.q_4_2, c.q_1_4,
            c.p_70, c.p_28, c.p_14, c.p_5, c.p_2,
            c.l_f, c.d_f, c.r_nkpr, c.r_vsp, c.l_pt, c.p_pt,
            c.q_600, c.q_320, c.q_220, c.q_120,
            c.s_t
        FROM calculations c
        JOIN equipment e ON e.id = c.equipment_id
        WHERE
            c.hazard_component = ?
            AND c.scenario_no = ?
            AND e.equipment_name = ?
        ORDER BY
            COALESCE(c.fatalities_count, 0) DESC,
            COALESCE(c.total_damage, 0) DESC,
            COALESCE(c.scenario_frequency, 0) DESC
        LIMIT 1
    """, (hazard_component, scenario_no, equipment_name))

    return cur.fetchone()  # tuple или None


def get_fatalities_injured_for_top_scenario(conn, hazard_component, scenario_no, equipment_name):
    """
    Возвращает (fatalities_count, injured_count) для заданного:
    - hazard_component
    - scenario_no
    - equipment_name

    Берём одну наиболее релевантную строку calculations.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.fatalities_count,
            c.injured_count
        FROM calculations c
        JOIN equipment e ON e.id = c.equipment_id
        WHERE
            c.hazard_component = ?
            AND c.scenario_no = ?
            AND e.equipment_name = ?
        ORDER BY
            COALESCE(c.fatalities_count, 0) DESC,
            COALESCE(c.injured_count, 0) DESC,
            COALESCE(c.total_damage, 0) DESC,
            COALESCE(c.scenario_frequency, 0) DESC
        LIMIT 1
    """, (hazard_component, scenario_no, equipment_name))

    return cur.fetchone()  # tuple (fatalities, injured) или None


def get_total_damage_for_top_scenario(conn, hazard_component, scenario_no, equipment_name):
    """
    Возвращает total_damage (тыс. руб) для заданного:
    - hazard_component
    - scenario_no
    - equipment_name

    Берём одну наиболее релевантную строку calculations.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.total_damage
        FROM calculations c
        JOIN equipment e ON e.id = c.equipment_id
        WHERE
            c.hazard_component = ?
            AND c.scenario_no = ?
            AND e.equipment_name = ?
        ORDER BY
            COALESCE(c.total_damage, 0) DESC,
            COALESCE(c.fatalities_count, 0) DESC,
            COALESCE(c.scenario_frequency, 0) DESC
        LIMIT 1
    """, (hazard_component, scenario_no, equipment_name))

    row = cur.fetchone()  # (total_damage,) или None
    return row[0] if row is not None else None


def get_ov_in_accident_for_top_scenario(conn, hazard_component, scenario_no, equipment_name):
    """
    Возвращает ov_in_accident_t (тонн) из calculations для заданного:
    - hazard_component
    - scenario_no
    - equipment_name
    Берём одну наиболее релевантную строку.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.ov_in_accident_t
        FROM calculations c
        JOIN equipment e ON e.id = c.equipment_id
        WHERE
            c.hazard_component = ?
            AND c.scenario_no = ?
            AND e.equipment_name = ?
        ORDER BY
            COALESCE(c.fatalities_count, 0) DESC,
            COALESCE(c.total_damage, 0) DESC,
            COALESCE(c.scenario_frequency, 0) DESC
        LIMIT 1
    """, (hazard_component, scenario_no, equipment_name))

    row = cur.fetchone()  # (ov_in_accident_t,) или None
    return row[0] if row is not None else None


def open_db(db_path):
    return sqlite3.connect(db_path)
