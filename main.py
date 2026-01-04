import json
import sqlite3
from pathlib import Path
from calculations import equipment_type_0_kind_0, equipment_type_1_kind_0, equipment_type_2_kind_0, equipment_type_3_kind_0

TYPICAL_SCENARIOS_PATH = Path("data/calc/typical_scenarios.json")  # при необходимости поправьте
DB_PATH = Path("data/iris.sqlite3")  # при необходимости поправьте


def is_pair_allowed(allowed_pairs: dict, equipment_type: int, kind: int) -> bool:
    """Если для пары есть явный запрет — запрещено. Если записи нет — считаем допустимым."""
    et = str(equipment_type)
    k = str(kind)
    rule = allowed_pairs.get(et, {}).get(k)
    if rule is None:
        return True
    return bool(rule.get("allowed", True))


def get_scenarios_for(scenarios_tree: dict, equipment_type: int, kind: int) -> list[dict]:
    return scenarios_tree.get(str(equipment_type), {}).get(str(kind), []) or []


def write_calculation(cur: sqlite3.Cursor, payload: dict) -> None:
    """
    Запись результата расчёта в таблицу calculations.
    payload — словарь, который вернул calc_for_scenario().
    """

    # Кэшируем список колонок calculations один раз
    if not hasattr(write_calculation, "_cols"):
        # PRAGMA table_info: (cid, name, type, notnull, dflt_value, pk)
        cols = [r[1] for r in cur.execute("PRAGMA table_info(calculations);").fetchall()]
        # id автоинкремент — не вставляем
        write_calculation._cols = [c for c in cols if c != "id"]

    cols = write_calculation._cols

    # Для отсутствующих ключей подставляем None
    values = [payload.get(c) for c in cols]

    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join(cols)

    cur.execute(
        f"INSERT INTO calculations ({col_list}) VALUES ({placeholders});",
        values,
    )


def main(db_path: Path = DB_PATH, typical_scenarios_path: Path = TYPICAL_SCENARIOS_PATH) -> None:
    # 0) загрузка типовых сценариев
    with typical_scenarios_path.open("r", encoding="utf-8") as f:
        typical = json.load(f)

    allowed_pairs = typical.get("meta", {}).get("allowed_pairs", {})
    scenarios_tree = typical.get("scenarios", {})

    # 1) подключение к БД
    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        # 1. очищаем calculations
        cur.execute("DELETE FROM calculations;")

        # 2. берем список оборудования (весь)
        # ВАЖНО: ниже выбираем все поля equipment + все поля substances (как минимум kind).
        equipment_rows = cur.execute(
            """
            SELECT
                e.*,
                s.*,
                e.id AS equipment_id  -- на случай пересечения имён колонок
            FROM equipment e
            JOIN substances s ON s.id = e.substance_id
            ORDER BY e.id
            """
        ).fetchall()

        if not equipment_rows:
            con.commit()
            return

        # 3. Перебираем оборудование в цикле
        for row in equipment_rows:
            # 3.1. Получаем свойства вещества в оборудовании
            # Поскольку мы сделали SELECT e.* + s.*, "substance properties" лежат в row.
            # Для читаемости выделим:
            equipment = row
            substance = row

            equipment_id = int(row["equipment_id"])
            equipment_name = row["equipment_name"]
            hazard_component = row["hazard_component"]
            equipment_type = int(row["equipment_type"])
            kind = int(row["kind"])

            # 3.2. Получаем перечень сценариев из typical_scenarios.json (по оборудованию и веществу)
            if not is_pair_allowed(allowed_pairs, equipment_type, kind):
                continue

            scenarios_list = get_scenarios_for(scenarios_tree, equipment_type, kind)
            if not scenarios_list:
                continue

            # 3.3. делаем print некоторых полей оборудования и вещества
            # (поля вещества можно расширить — зависит от вашей схемы substances)
            # print(
            #     f"[equipment_id={equipment_id}] "
            #     f"name={equipment_name!r} "
            #     f"hazard_component={hazard_component!r} "
            #     f"equipment_type={equipment_type} "
            #     f"substance_kind={kind}"
            # )

            # 3.4. По перечню сценариев делаем расчет (пока заглушим pass)

            # 3.5. Записываем в calculations (пока заглушим pass)
            for sc in scenarios_list:
                # следующий свободный scenario_no в таблице
                scenario_no_global = cur.execute(
                    "SELECT COALESCE(MAX(scenario_no), 0) + 1 FROM calculations;"
                ).fetchone()[0]
                # если вам нужно сохранять исходные частоты из json — можно собирать payload уже тут
                # а расчёт потом расширить
                if equipment["equipment_type"] == 0 and substance["kind"] == 0:
                    payload = equipment_type_0_kind_0.calc_for_scenario(equipment, substance, sc, scenario_no_global)
                elif equipment["equipment_type"] == 1 and substance["kind"] == 0:
                    payload = equipment_type_1_kind_0.calc_for_scenario(equipment, substance, sc, scenario_no_global)
                elif equipment["equipment_type"] == 2 and substance["kind"] == 0:
                    payload = equipment_type_2_kind_0.calc_for_scenario(equipment, substance, sc, scenario_no_global)
                elif equipment["equipment_type"] == 3 and substance["kind"] == 0:
                    payload = equipment_type_3_kind_0.calc_for_scenario(equipment, substance, sc, scenario_no_global)
                else:
                    continue

                write_calculation(cur, payload)



        con.commit()


if __name__ == "__main__":
    main()
