# models/substance/substance_db.py

import os
import sqlite3
import json

from .substance_model import Substance


from models.db.db_config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS substances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                kind INTEGER NOT NULL,
                formula TEXT,

                composition TEXT,
                physical TEXT,
                explosion TEXT,
                toxicity TEXT,

                reactivity TEXT,
                odor TEXT,
                corrosiveness TEXT,
                precautions TEXT,
                impact TEXT,
                protection TEXT,
                neutralization_methods TEXT,
                first_aid TEXT
            )
        """)
        conn.commit()


# --- CRUD ---

def create_substance(substance: Substance) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO substances (
                name, kind, formula,
                composition, physical, explosion, toxicity,
                reactivity, odor, corrosiveness, precautions, impact,
                protection, neutralization_methods, first_aid
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            substance.name,
            substance.kind,
            substance.formula,

            json.dumps(substance.composition, ensure_ascii=False),
            json.dumps(substance.physical, ensure_ascii=False),
            json.dumps(substance.explosion, ensure_ascii=False),
            json.dumps(substance.toxicity, ensure_ascii=False),

            substance.reactivity,
            substance.odor,
            substance.corrosiveness,
            substance.precautions,
            substance.impact,
            substance.protection,
            substance.neutralization_methods,
            substance.first_aid,
        ))
        conn.commit()
        return cur.lastrowid


def get_substance_by_id(substance_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM substances WHERE id = ?", (substance_id,))
        row = cur.fetchone()

    if row is None:
        return None

    return _row_to_substance(row)


def list_substances():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM substances ORDER BY id")
        rows = cur.fetchall()

    return [_row_to_substance(r) for r in rows]


def update_substance(substance: Substance) -> bool:
    """
    Обновляет запись по substance.id (заменой всех полей).
    Возвращает True если обновили, False если такой id нет.
    """
    if substance.id is None:
        return False

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE substances SET
                name = ?,
                kind = ?,
                formula = ?,

                composition = ?,
                physical = ?,
                explosion = ?,
                toxicity = ?,

                reactivity = ?,
                odor = ?,
                corrosiveness = ?,
                precautions = ?,
                impact = ?,
                protection = ?,
                neutralization_methods = ?,
                first_aid = ?
            WHERE id = ?
        """, (
            substance.name,
            substance.kind,
            substance.formula,

            json.dumps(substance.composition, ensure_ascii=False),
            json.dumps(substance.physical, ensure_ascii=False),
            json.dumps(substance.explosion, ensure_ascii=False),
            json.dumps(substance.toxicity, ensure_ascii=False),

            substance.reactivity,
            substance.odor,
            substance.corrosiveness,
            substance.precautions,
            substance.impact,
            substance.protection,
            substance.neutralization_methods,
            substance.first_aid,

            substance.id
        ))
        conn.commit()
        return cur.rowcount > 0


def delete_substance(substance_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM substances WHERE id = ?", (substance_id,))
        conn.commit()
        return cur.rowcount > 0


# --- Вспомогательные функции ---

def _row_to_substance(row):
    # Порядок полей совпадает с CREATE TABLE
    (
        id, name, kind, formula,
        composition, physical, explosion, toxicity,
        reactivity, odor, corrosiveness, precautions, impact,
        protection, neutralization_methods, first_aid
    ) = row

    return Substance(
        id=id,
        name=name,
        kind=kind,
        formula=formula or "",

        composition=json.loads(composition) if composition else None,
        physical=json.loads(physical) if physical else None,
        explosion=json.loads(explosion) if explosion else None,
        toxicity=json.loads(toxicity) if toxicity else None,

        reactivity=reactivity or "",
        odor=odor or "",
        corrosiveness=corrosiveness or "",
        precautions=precautions or "",
        impact=impact or "",
        protection=protection or "",
        neutralization_methods=neutralization_methods or "",
        first_aid=first_aid or "",
    )


def seed_default_substances_if_empty():
    """
    Создаёт вещества с максимально заполненными свойствами:
    - Бензин
    - Хлор (жидкий)
    - СУГ
    Только если таблица пустая.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM substances")
        if cur.fetchone()[0] > 0:
            return

    # ---------- БЕНЗИН ----------
    gasoline = Substance(
        name="Бензин",
        kind=0,
        formula="Смесь углеводородов C5–C12",

        composition={
            "components": [
                {"name": "алканы", "mass_fraction": 0.6},
                {"name": "арены", "mass_fraction": 0.25},
                {"name": "олефины", "mass_fraction": 0.15},
            ],
            "notes": "Типовой автомобильный бензин"
        },

        physical={
            "molar_mass_kg_per_mol": 0.114,
            "density_liquid_kg_per_m3": 730,
            "density_gas_kg_per_m3": None,
            "evaporation_heat_J_per_kg": 350000,
            "boiling_point_C": 30,
        },

        explosion={
            "flash_point_C": -40,
            "lel_percent": 1.2,
            "autoignition_temp_C": 280,
            "energy_reserve_factor": 1,
            "expansion_degree": 4,
            "heat_of_combustion_kJ_per_kg": 44000,
            "burning_rate_kg_per_s_m2": 0.05,
        },

        toxicity={
            "hazard_class": 4,
            "pdk_mg_per_m3": 100,
            "lethal_tox_dose_mg_min_per_L": None,
            "threshold_tox_dose_mg_min_per_L": None,
        },

        reactivity="Химически устойчив",
        odor="Характерный бензиновый",
        corrosiveness="Неагрессивен",
        precautions="Исключить источники воспламенения",
        impact="Наркотическое действие при вдыхании",
        protection="Фильтрующий противогаз",
        neutralization_methods="Сбор, инертирование",
        first_aid="Вывести на свежий воздух",
    )

    # ---------- ХЛОР (ЖИДКИЙ) ----------
    chlorine = Substance(
        name="Хлор (жидкий)",
        kind=8,
        formula="Cl₂",

        composition={
            "components": [{"name": "хлор", "mass_fraction": 1.0}],
            "notes": "Технический хлор"
        },

        physical={
            "molar_mass_kg_per_mol": 0.0709,
            "density_liquid_kg_per_m3": 1460,
            "density_gas_kg_per_m3": 3.21,
            "evaporation_heat_J_per_kg": 287000,
            "boiling_point_C": -34.6,
        },

        explosion={
            "flash_point_C": None,
            "lel_percent": None,
            "autoignition_temp_C": None,
            "energy_reserve_factor": None,
            "expansion_degree": 7,
            "heat_of_combustion_kJ_per_kg": None,
            "burning_rate_kg_per_s_m2": None,
        },

        toxicity={
            "hazard_class": 2,
            "pdk_mg_per_m3": 1,
            "lethal_tox_dose_mg_min_per_L": 300,
            "threshold_tox_dose_mg_min_per_L": 50,
        },

        reactivity="Сильный окислитель",
        odor="Резкий удушающий",
        corrosiveness="Сильно коррозионно-активен",
        precautions="Работа только в СИЗ",
        impact="Поражение дыхательных путей",
        protection="Изолирующий противогаз",
        neutralization_methods="Щелочные растворы",
        first_aid="Немедленно на свежий воздух, кислород",
    )

    # ---------- СУГ ----------
    sug = Substance(
        name="СУГ",
        kind=4,
        formula="C₃H₈–C₄H₁₀",

        composition={
            "components": [
                {"name": "пропан", "mass_fraction": 0.6},
                {"name": "бутан", "mass_fraction": 0.4},
            ],
            "notes": "Сжиженный углеводородный газ"
        },

        physical={
            "molar_mass_kg_per_mol": 0.048,
            "density_liquid_kg_per_m3": 520,
            "density_gas_kg_per_m3": 1.9,
            "evaporation_heat_J_per_kg": 360000,
            "boiling_point_C": -42,
        },

        explosion={
            "flash_point_C": -90,
            "lel_percent": 2.1,
            "autoignition_temp_C": 470,
            "energy_reserve_factor": 2,
            "expansion_degree": 7,
            "heat_of_combustion_kJ_per_kg": 46000,
            "burning_rate_kg_per_s_m2": 0.08,
        },

        toxicity={
            "hazard_class": 4,
            "pdk_mg_per_m3": None,
            "lethal_tox_dose_mg_min_per_L": None,
            "threshold_tox_dose_mg_min_per_L": None,
        },

        reactivity="Химически устойчив",
        odor="Запах одоранта",
        corrosiveness="Неагрессивен",
        precautions="Контроль утечек",
        impact="Асфиксия при высоких концентрациях",
        protection="Фильтрующий противогаз",
        neutralization_methods="Проветривание, инертирование",
        first_aid="Вывести на свежий воздух",
    )

    create_substance(gasoline)
    create_substance(chlorine)
    create_substance(sug)

