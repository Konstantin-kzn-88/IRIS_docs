# calculations/amount_of_substance.py

import os
import sqlite3
import json

from models.db.db_config import DB_PATH

# Метки типов оборудования (для "наименование оборудования")
EQUIPMENT_TYPE_LABELS = {
    0: "Трубопровод",
    1: "РВС",
    2: "Аппарат под давлением",
    3: "Колонна",
    4: "Насос",
    5: "Компрессор",
    6: "Теплообменник",
    7: "Цистерна",
}

# Типы, где считаем по формуле объем/заполнение/плотности
FORMULA_TYPES = {0, 1, 2, 3, 6, 7}





def get_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_amount_table(conn: sqlite3.Connection):
    """
    Создать таблицу, если нет.
    Если есть — полностью очистить.
    """
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hazardous_amounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            equipment_id INTEGER NOT NULL,
            equipment_name TEXT NOT NULL,
            substance_name TEXT NOT NULL,

            amount_t REAL NOT NULL,

            phase_state TEXT,
            temperature_c REAL,
            pressure_mpa REAL
        )
    """)
    # Полностью очищаем таблицу
    cur.execute("DELETE FROM hazardous_amounts")
    conn.commit()


def calculate_amount_t(equipment_type: int, volume_m3, fill_fraction, density_liq, density_gas) -> float:
    """
    Возвращает количество вещества в тоннах.
    """
    # Насос
    if equipment_type == 4:
        return 0.1

    # Компрессор
    if equipment_type == 5:
        return 0.05

    # По формуле (0,1,2,3,6,7)
    if equipment_type in FORMULA_TYPES:
        V = volume_m3 if volume_m3 is not None else 0.0
        f = fill_fraction if fill_fraction is not None else 0.0

        rho_l = density_liq if density_liq is not None else 0.0
        rho_g = density_gas if density_gas is not None else 0.0

        mass_kg = V * f * rho_l + V * (1.0 - f) * rho_g
        mass_t = mass_kg / 1000.0
        return mass_t

    # На всякий случай: неизвестный тип
    return 0.0


def recalc_hazardous_amounts(db_path: str | None = None):
    """
    1) Создаёт таблицу hazardous_amounts (если нет)
    2) Если есть — очищает
    3) Пересчитывает количество по всем equipment
    4) Записывает результат в hazardous_amounts
    """
    if db_path is None:
        db_path = DB_PATH

    with get_connection(db_path) as conn:
        init_amount_table(conn)

        cur = conn.cursor()

        # Берём оборудование + вещество (substances.physical хранится JSON-строкой)
        cur.execute("""
            SELECT
                e.id,
                e.equipment_type,
                e.volume_m3,
                e.fill_fraction,
                e.phase_state,
                e.substance_temperature_c,
                e.pressure_mpa,

                s.name,
                s.physical
            FROM equipment e
            JOIN substances s ON s.id = e.substance_id
            ORDER BY e.id
        """)
        rows = cur.fetchall()

        for (
            eq_id,
            eq_type,
            volume_m3,
            fill_fraction,
            phase_state,
            temp_c,
            pressure_mpa,
            substance_name,
            physical_json
        ) in rows:

            physical = json.loads(physical_json) if physical_json else {}
            density_liq = physical.get("density_liquid_kg_per_m3")
            density_gas = physical.get("density_gas_kg_per_m3")

            amount_t = calculate_amount_t(
                equipment_type=eq_type,
                volume_m3=volume_m3,
                fill_fraction=fill_fraction,
                density_liq=density_liq,
                density_gas=density_gas
            )

            equipment_name = f"{EQUIPMENT_TYPE_LABELS.get(eq_type, 'Оборудование')} #{eq_id}"

            cur.execute("""
                INSERT INTO hazardous_amounts (
                    equipment_id,
                    equipment_name,
                    substance_name,
                    amount_t,
                    phase_state,
                    temperature_c,
                    pressure_mpa
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                eq_id,
                equipment_name,
                substance_name,
                amount_t,
                phase_state,
                temp_c,
                pressure_mpa
            ))

        conn.commit()
