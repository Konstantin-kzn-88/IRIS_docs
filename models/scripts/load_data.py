# scripts/load_data.py

import sqlite3
from models.db.db_config import DB_PATH

from models.substance import (
    init_db as init_substances_db,
    create_substance,
    Substance,
)

from models.equipment import (
    init_db as init_equipment_db,
    create_equipment,
    Equipment,
)

from models.calculations.amount_of_substance import recalc_hazardous_amounts


# -----------------------------
# 1) СЛОВАРИ ДАННЫХ
# -----------------------------

SUBSTANCES_DATA = [
    {
        "name": "Бензин",
        "kind": 0,
        "formula": "Смесь углеводородов C5–C12",
        "composition": {
            "components": [
                {"name": "алканы", "mass_fraction": 0.6},
                {"name": "арены", "mass_fraction": 0.25},
                {"name": "олефины", "mass_fraction": 0.15},
            ],
            "notes": "Типовой автомобильный бензин",
        },
        "physical": {
            "molar_mass_kg_per_mol": 0.114,
            "density_liquid_kg_per_m3": 730,
            "density_gas_kg_per_m3": None,
            "evaporation_heat_J_per_kg": 350000,
            "boiling_point_C": 30,
        },
        "explosion": {
            "flash_point_C": -40,
            "lel_percent": 1.2,
            "autoignition_temp_C": 280,
            "energy_reserve_factor": 1,
            "expansion_degree": 4,
            "heat_of_combustion_kJ_per_kg": 44000,
            "burning_rate_kg_per_s_m2": 0.05,
        },
        "toxicity": {
            "hazard_class": 4,
            "pdk_mg_per_m3": 100,
            "lethal_tox_dose_mg_min_per_L": None,
            "threshold_tox_dose_mg_min_per_L": None,
        },
        "reactivity": "Химически устойчив",
        "odor": "Характерный бензиновый",
        "corrosiveness": "Неагрессивен",
        "precautions": "Исключить источники воспламенения",
        "impact": "Наркотическое действие при вдыхании",
        "protection": "Фильтрующий противогаз",
        "neutralization_methods": "Сбор, инертирование",
        "first_aid": "Вывести на свежий воздух",
    },
    {
        "name": "Хлор (жидкий)",
        "kind": 8,
        "formula": "Cl2",
        "composition": {
            "components": [{"name": "хлор", "mass_fraction": 1.0}],
            "notes": "Технический хлор",
        },
        "physical": {
            "molar_mass_kg_per_mol": 0.0709,
            "density_liquid_kg_per_m3": 1460,
            "density_gas_kg_per_m3": 3.21,
            "evaporation_heat_J_per_kg": 287000,
            "boiling_point_C": -34.6,
        },
        "explosion": {
            "flash_point_C": None,
            "lel_percent": None,
            "autoignition_temp_C": None,
            "energy_reserve_factor": None,
            "expansion_degree": 7,
            "heat_of_combustion_kJ_per_kg": None,
            "burning_rate_kg_per_s_m2": None,
        },
        "toxicity": {
            "hazard_class": 2,
            "pdk_mg_per_m3": 1,
            "lethal_tox_dose_mg_min_per_L": 300,
            "threshold_tox_dose_mg_min_per_L": 50,
        },
        "reactivity": "Сильный окислитель",
        "odor": "Резкий удушающий",
        "corrosiveness": "Сильно коррозионно-активен",
        "precautions": "Работа только в СИЗ",
        "impact": "Поражение дыхательных путей",
        "protection": "Изолирующий противогаз",
        "neutralization_methods": "Щелочные растворы",
        "first_aid": "Свежий воздух, кислород, медпомощь",
    },
    {
        "name": "СУГ",
        "kind": 4,
        "formula": "C3H8–C4H10",
        "composition": {
            "components": [
                {"name": "пропан", "mass_fraction": 0.6},
                {"name": "бутан", "mass_fraction": 0.4},
            ],
            "notes": "Сжиженный углеводородный газ",
        },
        "physical": {
            "molar_mass_kg_per_mol": 0.048,
            "density_liquid_kg_per_m3": 520,
            "density_gas_kg_per_m3": 1.9,
            "evaporation_heat_J_per_kg": 360000,
            "boiling_point_C": -42,
        },
        "explosion": {
            "flash_point_C": -90,
            "lel_percent": 2.1,
            "autoignition_temp_C": 470,
            "energy_reserve_factor": 2,
            "expansion_degree": 7,
            "heat_of_combustion_kJ_per_kg": 46000,
            "burning_rate_kg_per_s_m2": 0.08,
        },
        "toxicity": {
            "hazard_class": 4,
            "pdk_mg_per_m3": None,
            "lethal_tox_dose_mg_min_per_L": None,
            "threshold_tox_dose_mg_min_per_L": None,
        },
        "reactivity": "Химически устойчив",
        "odor": "Запах одоранта",
        "corrosiveness": "Неагрессивен",
        "precautions": "Контроль утечек",
        "impact": "Асфиксия при высоких концентрациях",
        "protection": "Фильтрующий противогаз",
        "neutralization_methods": "Проветривание, инертирование",
        "first_aid": "Вывести на свежий воздух",
    },
]

# Оборудование задаём словарём: ключ = имя вещества,
# значение = список объектов оборудования под это вещество.
# equipment_type: 0..7 (обязательное требование)
EQUIPMENT_DATA = {
    "Бензин": [
        # Пример: трубопровод с 3 точками (6 координат)
        {
            "equipment_type": 0,
            "coord_type": 0,
            "phase_state": "ж.ф.",
            "coordinates": [0, 0, 50, 0, 100, 20],
            "length_m": 120.0,
            "diameter_mm": 200.0,
            "wall_thickness_mm": 6.0,
            "volume_m3": 10.0,
            "fill_fraction": 0.8,
            "pressure_mpa": 0.2,
            "spill_coefficient": 0.9,
            "spill_area_m2": 120.0,
            "substance_temperature_c": 20.0,
            "shutdown_time_s": 60.0,
            "evaporation_time_s": 3600.0,
        },
        # Дальше можно добавлять ещё записи — но по вашему требованию
        # мы создадим типы 0..7 программно, см. ниже.
    ],
    "Хлор (жидкий)": [],
    "СУГ": [],
}


# -----------------------------
# 2) ВСПОМОГАТЕЛЬНЫЕ SQL
# -----------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def clear_table(table_name: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name}")
        conn.commit()


def get_substance_id_by_name(name: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM substances WHERE name = ?", (name,))
        row = cur.fetchone()
        return row[0] if row else None


# -----------------------------
# 3) ЗАГРУЗКА ВЕЩЕСТВ
# -----------------------------

def load_substances_from_dict(clear_substances: bool = False, load_substances: bool = True):
    init_substances_db()

    if clear_substances:
        # Важно: сначала чистим equipment, иначе FK не даст удалить вещества
        clear_table("equipment")
        clear_table("substances")

    if not load_substances:
        return

    for d in SUBSTANCES_DATA:
        s = Substance(
            name=d["name"],
            kind=d["kind"],
            formula=d.get("formula", ""),
            composition=d.get("composition"),
            physical=d.get("physical"),
            explosion=d.get("explosion"),
            toxicity=d.get("toxicity"),
            reactivity=d.get("reactivity", ""),
            odor=d.get("odor", ""),
            corrosiveness=d.get("corrosiveness", ""),
            precautions=d.get("precautions", ""),
            impact=d.get("impact", ""),
            protection=d.get("protection", ""),
            neutralization_methods=d.get("neutralization_methods", ""),
            first_aid=d.get("first_aid", ""),
        )
        create_substance(s)


# -----------------------------
# 4) ЗАГРУЗКА ОБОРУДОВАНИЯ
# -----------------------------

def load_equipment_from_dict(clear_equipment: bool = True):
    init_equipment_db()

    if clear_equipment:
        clear_table("equipment")

    # Требование: под каждое вещество создать EQUIPMENT_TYPES 0..7
    required_types = list(range(0, 8))

    for substance_name in ["Бензин", "Хлор (жидкий)", "СУГ"]:
        sid = get_substance_id_by_name(substance_name)
        if sid is None:
            # Если вещества нет — пропускаем (чтобы скрипт не падал)
            continue

        # Берём “шаблонные” записи, если пользователь их дал
        templates = EQUIPMENT_DATA.get(substance_name, [])

        # Для новичка: создаём 8 записей (типы 0..7).
        # Если есть шаблон для какого-то типа — используем его, иначе создаём дефолт.
        template_by_type = {t.get("equipment_type"): t for t in templates}

        for eq_type in required_types:
            t = template_by_type.get(eq_type, {})

            # Простейшие дефолты (чтобы всё было заполнено)
            if substance_name == "СУГ":
                phase_state = t.get("phase_state", "ж.ф.+г.ф.")
            elif substance_name == "Хлор (жидкий)":
                phase_state = t.get("phase_state", "ж.ф.")
            else:
                phase_state = t.get("phase_state", "ж.ф.")

            coord_type = t.get("coord_type", 1)  # стационарный по умолчанию
            coords = t.get("coordinates", [10 * eq_type, 10 * eq_type])  # хотя бы одна точка

            eq = Equipment(
                substance_id=sid,
                equipment_type=eq_type,
                coord_type=coord_type,
                phase_state=phase_state,
                coordinates=coords,

                length_m=t.get("length_m", 50.0 if eq_type == 0 else None),
                diameter_mm=t.get("diameter_mm", 200.0 if eq_type == 0 else None),
                wall_thickness_mm=t.get("wall_thickness_mm", 6.0 if eq_type == 0 else None),

                volume_m3=t.get("volume_m3", 25.0 if eq_type in (1, 2, 3, 7) else 5.0),
                fill_fraction=t.get("fill_fraction", 0.8),

                pressure_mpa=t.get("pressure_mpa", 0.6 if eq_type in (2, 3, 5) else 0.2),

                spill_coefficient=t.get("spill_coefficient", 0.9),
                spill_area_m2=t.get("spill_area_m2", 120.0),
                substance_temperature_c=t.get("substance_temperature_c", 20.0),
                shutdown_time_s=t.get("shutdown_time_s", 60.0),
                evaporation_time_s=t.get("evaporation_time_s", 3600.0),
            )

            create_equipment(eq)


# -----------------------------
# 5) ГЛАВНЫЙ ЗАПУСК
# -----------------------------

def run_loader(
    clear_equipment: bool = True,
    clear_substances: bool = False,
    load_substances: bool = True
):
    # 1) вещества (опционально чистим и загружаем)
    load_substances_from_dict(clear_substances=clear_substances, load_substances=load_substances)

    # 2) оборудование (чистим всегда по вашему пункту, если clear_equipment=True)
    load_equipment_from_dict(clear_equipment=clear_equipment)

    # 3) пересчёт hazardous_amounts (таблица создаётся/очищается внутри расчёта)
    recalc_hazardous_amounts()
    print("OK: hazardous_amounts обновлена")


if __name__ == "__main__":
    # Настройки по умолчанию:
    # - очищаем оборудование
    # - вещества не очищаем
    # - вещества загружаем
    run_loader(
        clear_equipment=True,
        clear_substances=False,
        load_substances=True
    )