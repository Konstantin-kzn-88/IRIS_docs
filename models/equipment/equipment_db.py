# models/equipment/equipment_db.py

import os
import sqlite3
import json

from .equipment_model import Equipment, EQUIPMENT_TYPES

from models.db.db_config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # На всякий случай включим foreign keys (если будут добавлены)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                substance_id INTEGER NOT NULL,

                phase_state TEXT,
                coord_type INTEGER,
                equipment_type INTEGER,

                coordinates TEXT,   -- JSON: [x1, y1, x2, y2, ...]

                length_m REAL,
                diameter_mm REAL,
                wall_thickness_mm REAL,
                volume_m3 REAL,
                fill_fraction REAL,

                pressure_mpa REAL,

                spill_coefficient REAL,
                spill_area_m2 REAL,
                substance_temperature_c REAL,
                shutdown_time_s REAL,
                evaporation_time_s REAL,

                FOREIGN KEY (substance_id)
                    REFERENCES substances(id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            )
        """)
        conn.commit()


# ---------------- CRUD ----------------

def create_equipment(eq: Equipment) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO equipment (
                substance_id,
                phase_state, coord_type, equipment_type,
                coordinates,
                length_m, diameter_mm, wall_thickness_mm, volume_m3, fill_fraction,
                pressure_mpa,
                spill_coefficient, spill_area_m2, substance_temperature_c,
                shutdown_time_s, evaporation_time_s
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            eq.substance_id,
            eq.phase_state,
            eq.coord_type,
            eq.equipment_type,
            json.dumps(eq.coordinates),
            eq.length_m,
            eq.diameter_mm,
            eq.wall_thickness_mm,
            eq.volume_m3,
            eq.fill_fraction,
            eq.pressure_mpa,
            eq.spill_coefficient,
            eq.spill_area_m2,
            eq.substance_temperature_c,
            eq.shutdown_time_s,
            eq.evaporation_time_s
        ))
        conn.commit()
        return cur.lastrowid


def get_equipment_by_id(equipment_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,))
        row = cur.fetchone()

    if row is None:
        return None

    return _row_to_equipment(row)


def list_equipment():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM equipment ORDER BY id")
        rows = cur.fetchall()

    return [_row_to_equipment(r) for r in rows]


def update_equipment(eq: Equipment) -> bool:
    if eq.id is None:
        return False

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE equipment SET
                substance_id = ?,
                phase_state = ?,
                coord_type = ?,
                equipment_type = ?,
                length_m = ?,
                diameter_mm = ?,
                wall_thickness_mm = ?,
                volume_m3 = ?,
                fill_fraction = ?,
                pressure_mpa = ?,
                spill_coefficient = ?,
                spill_area_m2 = ?,
                substance_temperature_c = ?,
                shutdown_time_s = ?,
                evaporation_time_s = ?
            WHERE id = ?
        """, (
            eq.substance_id,
            eq.phase_state,
            eq.coord_type,
            eq.equipment_type,
            eq.length_m,
            eq.diameter_mm,
            eq.wall_thickness_mm,
            eq.volume_m3,
            eq.fill_fraction,
            eq.pressure_mpa,
            eq.spill_coefficient,
            eq.spill_area_m2,
            eq.substance_temperature_c,
            eq.shutdown_time_s,
            eq.evaporation_time_s,
            eq.id
        ))
        conn.commit()
        return cur.rowcount > 0


def delete_equipment(equipment_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
        conn.commit()
        return cur.rowcount > 0


def _row_to_equipment(row):
    (
        id,
        substance_id,
        phase_state,
        coord_type,
        equipment_type,
        coordinates,
        length_m,
        diameter_mm,
        wall_thickness_mm,
        volume_m3,
        fill_fraction,
        pressure_mpa,
        spill_coefficient,
        spill_area_m2,
        substance_temperature_c,
        shutdown_time_s,
        evaporation_time_s
    ) = row

    return Equipment(
        id=id,
        substance_id=substance_id,
        phase_state=phase_state,
        coord_type=coord_type,
        equipment_type=equipment_type,
        coordinates=json.loads(coordinates) if coordinates else [],
        length_m=length_m,
        diameter_mm=diameter_mm,
        wall_thickness_mm=wall_thickness_mm,
        volume_m3=volume_m3,
        fill_fraction=fill_fraction,
        pressure_mpa=pressure_mpa,
        spill_coefficient=spill_coefficient,
        spill_area_m2=spill_area_m2,
        substance_temperature_c=substance_temperature_c,
        shutdown_time_s=shutdown_time_s,
        evaporation_time_s=evaporation_time_s
    )


# ---------------- Seed (создание оборудования под вещества) ----------------

def _get_substance_id_by_name(name: str):
    """
    Берём id вещества по имени из таблицы substances.
    Предполагается, что модуль substances уже создал и заполнил таблицу.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM substances WHERE name = ?", (name,))
        row = cur.fetchone()
        return row[0] if row else None


def seed_equipment_for_default_substances_if_empty():
    """
    Создаёт оборудование (типы 0..7) для каждого из веществ:
    - Бензин
    - Хлор (жидкий)
    - СУГ

    Делает это только если таблица equipment пустая.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM equipment")
        count = cur.fetchone()[0]

    if count > 0:
        return

    # Вещества (имена должны совпадать с тем, как вы их занесли в substances)
    targets = ["Бензин", "Хлор (жидкий)", "СУГ"]

    for substance_name in targets:
        sid = _get_substance_id_by_name(substance_name)
        if sid is None:
            # Если вещества нет в substances — пропускаем (чтобы не падало)
            continue

        for eq_type in EQUIPMENT_TYPES:
            # Заполним "максимально" (просто чтобы было не None)
            eq = Equipment(
                substance_id=sid,
                phase_state="ж.ф." if substance_name != "СУГ" else "ж.ф.+г.ф.",
                coord_type=1,                 # стационарный
                equipment_type=eq_type,

                length_m=50.0 if eq_type == 0 else None,   # длина для трубопровода
                diameter_mm=200.0 if eq_type == 0 else None,
                wall_thickness_mm=6.0 if eq_type == 0 else None,

                volume_m3=25.0 if eq_type in (1, 2, 3, 7) else 5.0,
                fill_fraction=0.8,

                pressure_mpa=0.6 if eq_type in (2, 3, 5) else 0.2,

                spill_coefficient=0.9,
                spill_area_m2=120.0,
                substance_temperature_c=20.0,
                shutdown_time_s=60.0,
                evaporation_time_s=3600.0
            )
            create_equipment(eq)
