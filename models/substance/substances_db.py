"""
Модуль SQLite CRUD для веществ (Substance).

Цели:
- Максимально простой код: sqlite3 из стандартной библиотеки, без dataclass/ORM.
- Храним "сложные" разделы (composition/physical/explosion/toxicity) как JSON-строки в SQLite.
  Это НЕ "загрузка из JSON-файла" — это просто способ положить словари в TEXT-поля базы.

Как использовать:
1) Убедитесь, что substance.py (класс Substance) лежит рядом с этим файлом.
2) Запустите:
   python substances_db.py
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from substance import Substance


# -----------------------------
# Настройки БД
# -----------------------------

DEFAULT_DB_PATH = "substances.sqlite"  # имя файла базы данных по умолчанию


def _dict_to_json(value: Dict[str, Any]) -> str:
    """
    Преобразовать словарь в JSON-строку.
    ensure_ascii=False — чтобы кириллица сохранялась нормально.
    """
    return json.dumps(value, ensure_ascii=False)


def _json_to_dict(value: str) -> Dict[str, Any]:
    """Преобразовать JSON-строку обратно в словарь."""
    if value is None or value == "":
        return {}
    return json.loads(value)


def connect(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Открыть соединение с SQLite.

    db_path — путь к файлу базы.
    Возвращает объект соединения, через который выполняются запросы.
    """
    connection = sqlite3.connect(db_path)
    # row_factory позволяет получать строки как "словарь" (доступ по именам колонок)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    """
    Создать таблицу substances, если её ещё нет.

    Важно:
    - composition/physical/explosion/toxicity храним как TEXT (JSON).
    - Остальные поля — обычный TEXT/INTEGER.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS substances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Общие поля
        name TEXT NOT NULL,
        kind INTEGER NOT NULL,
        formula TEXT,

        -- Сложные разделы в JSON
        composition_json TEXT,
        physical_json TEXT,
        explosion_json TEXT,
        toxicity_json TEXT,

        -- Прочие описательные поля
        reactivity TEXT,
        odor TEXT,
        corrosiveness TEXT,
        precautions TEXT,
        impact TEXT,
        protection TEXT,
        neutralization_methods TEXT,
        first_aid TEXT
    );
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()


# -----------------------------
# CRUD операции
# -----------------------------

def create_substance(connection: sqlite3.Connection, substance: Substance) -> int:
    """
    CREATE: добавить вещество в базу.

    Возвращает id добавленной записи.
    """
    sql = """
    INSERT INTO substances (
        name, kind, formula,
        composition_json, physical_json, explosion_json, toxicity_json,
        reactivity, odor, corrosiveness, precautions, impact, protection,
        neutralization_methods, first_aid
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cursor = connection.cursor()

    # Важно: "сложные" разделы — это словари -> JSON строка
    composition_json = _dict_to_json(substance.composition)
    physical_json = _dict_to_json(substance.physical)
    explosion_json = _dict_to_json(substance.explosion)
    toxicity_json = _dict_to_json(substance.toxicity)

    cursor.execute(
        sql,
        (
            substance.name,
            substance.kind,
            substance.formula,
            composition_json,
            physical_json,
            explosion_json,
            toxicity_json,
            substance.reactivity,
            substance.odor,
            substance.corrosiveness,
            substance.precautions,
            substance.impact,
            substance.protection,
            substance.neutralization_methods,
            substance.first_aid,
        ),
    )
    connection.commit()

    # lastrowid — id последней добавленной строки
    return int(cursor.lastrowid)


def _row_to_substance(row: sqlite3.Row) -> Substance:
    """
    Внутренняя функция: преобразовать строку SQLite (Row) в объект Substance.
    """
    data: Dict[str, Any] = {
        "name": row["name"],
        "kind": row["kind"],
        "formula": row["formula"] or "",
        "composition": _json_to_dict(row["composition_json"] or ""),
        "physical": _json_to_dict(row["physical_json"] or ""),
        "explosion": _json_to_dict(row["explosion_json"] or ""),
        "toxicity": _json_to_dict(row["toxicity_json"] or ""),
        "reactivity": row["reactivity"] or "",
        "odor": row["odor"] or "",
        "corrosiveness": row["corrosiveness"] or "",
        "precautions": row["precautions"] or "",
        "impact": row["impact"] or "",
        "protection": row["protection"] or "",
        "neutralization_methods": row["neutralization_methods"] or "",
        "first_aid": row["first_aid"] or "",
    }
    return Substance.from_dict(data)


def get_substance_by_id(connection: sqlite3.Connection, substance_id: int) -> Optional[Tuple[int, Substance]]:
    """
    READ: получить вещество по id.

    Возвращает:
    - (id, Substance), если найдено
    - None, если записи нет
    """
    sql = "SELECT * FROM substances WHERE id = ?;"
    cursor = connection.cursor()
    cursor.execute(sql, (substance_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return (int(row["id"]), _row_to_substance(row))


def list_substances(connection: sqlite3.Connection, limit: int = 100, offset: int = 0) -> List[Tuple[int, Substance]]:
    """
    READ (список): получить несколько веществ.

    limit — сколько записей вернуть максимум
    offset — смещение (для постраничного вывода)
    """
    sql = "SELECT * FROM substances ORDER BY id ASC LIMIT ? OFFSET ?;"
    cursor = connection.cursor()
    cursor.execute(sql, (limit, offset))
    rows = cursor.fetchall()

    result: List[Tuple[int, Substance]] = []
    for row in rows:
        result.append((int(row["id"]), _row_to_substance(row)))
    return result


def update_substance_by_id(connection: sqlite3.Connection, substance_id: int, substance: Substance) -> bool:
    """
    UPDATE: обновить запись по id.

    Возвращает True, если запись была обновлена (id существовал),
    иначе False.
    """
    sql = """
    UPDATE substances SET
        name = ?,
        kind = ?,
        formula = ?,
        composition_json = ?,
        physical_json = ?,
        explosion_json = ?,
        toxicity_json = ?,
        reactivity = ?,
        odor = ?,
        corrosiveness = ?,
        precautions = ?,
        impact = ?,
        protection = ?,
        neutralization_methods = ?,
        first_aid = ?
    WHERE id = ?;
    """
    cursor = connection.cursor()

    cursor.execute(
        sql,
        (
            substance.name,
            substance.kind,
            substance.formula,
            _dict_to_json(substance.composition),
            _dict_to_json(substance.physical),
            _dict_to_json(substance.explosion),
            _dict_to_json(substance.toxicity),
            substance.reactivity,
            substance.odor,
            substance.corrosiveness,
            substance.precautions,
            substance.impact,
            substance.protection,
            substance.neutralization_methods,
            substance.first_aid,
            substance_id,
        ),
    )
    connection.commit()

    # cursor.rowcount — сколько строк затронуто последним запросом
    return cursor.rowcount > 0


def delete_substance_by_id(connection: sqlite3.Connection, substance_id: int) -> bool:
    """
    DELETE: удалить запись по id.

    Возвращает True, если удалили (id существовал),
    иначе False.
    """
    sql = "DELETE FROM substances WHERE id = ?;"
    cursor = connection.cursor()
    cursor.execute(sql, (substance_id,))
    connection.commit()
    return cursor.rowcount > 0


# -----------------------------
# Пример запуска (main)
# -----------------------------

def main() -> None:
    """
    Пример того, как пользоваться CRUD функциями.
    Запускайте этот файл напрямую: python substances_db.py
    """
    db_path = DEFAULT_DB_PATH

    # 1) Подключаемся к базе и создаём таблицу
    connection = connect(db_path)
    init_db(connection)

    # 2) Создаём пример вещества
    benzine = Substance(
        name="Бензин (пример для БД)",
        kind=0,
        formula="Смешанная (углеводороды)",
        odor="Характерный бензиновый запах",
        precautions="Исключить источники зажигания; обеспечить вентиляцию; заземление при перекачке.",
        first_aid="Вывести на свежий воздух; при попадании на кожу — промыть водой с мылом; при симптомах — медпомощь.",
    )

    # Пример заполнения разделов (как в substance.py)
    benzine.physical["density_liquid_kg_per_m3"] = 740.0
    benzine.explosion["flash_point_C"] = -40.0
    benzine.explosion["lel_percent"] = 1.4
    benzine.toxicity["hazard_class"] = 3
    benzine.toxicity["pdk_mg_per_m3"] = 300.0

    # 3) CREATE
    new_id = create_substance(connection, benzine)
    print(f"[CREATE] Добавили вещество, id={new_id}")

    # 4) READ (по id)
    found = get_substance_by_id(connection, new_id)
    if found is None:
        print("[READ] Не найдено (неожиданно)")
    else:
        substance_id, substance_obj = found
        print(f"[READ] id={substance_id} -> {substance_obj}")

    # 5) UPDATE (по id)
    # Меняем пару полей и обновляем
    benzine.precautions = "Обеспечить вентиляцию; не курить; хранить в плотно закрытой таре."
    benzine.explosion["autoignition_temp_C"] = 280.0

    updated = update_substance_by_id(connection, new_id, benzine)
    print(f"[UPDATE] Обновление id={new_id}: {updated}")

    # 6) LIST
    print("\n[LIST] Текущие вещества в базе:")
    for substance_id, substance_obj in list_substances(connection, limit=50, offset=0):
        print(f"  - id={substance_id}: {substance_obj.name} ({substance_obj.kind_name()})")

    # 7) DELETE
    deleted = delete_substance_by_id(connection, new_id)
    print(f"\n[DELETE] Удаление id={new_id}: {deleted}")

    # Закрываем соединение (хорошая практика)
    connection.close()


if __name__ == "__main__":
    main()
