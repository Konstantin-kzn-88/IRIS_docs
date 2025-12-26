# substance_amounts.py
"""Заполнение таблицы hazardous_substance_amounts в БД iris.sqlite3.

Процедура:
1) Очищаем полностью таблицу hazardous_substance_amounts от записей.
2) Вычисляем массу ОВ в оборудовании:
   а) Для емкостного оборудования:
      m = volume_m3*fill_fraction*density_liquid_kg_per_m3
        + volume_m3*(1-fill_fraction)*density_gas_kg_per_m3
   б) Для трубопроводов:
      V = π*(d_in/2)^2*L,
      d_in = (diameter_mm - 2*wall_thickness_mm) / 1000.
      Далее масса определяется по фазовому состоянию (ж.ф./г.ф./ж.ф.+г.ф.).
   в) У насосов ставим по умолчанию 0,05 т.
   г) У компрессоров ставим по умолчанию 0,01 т.
3) Записываем результат в hazardous_substance_amounts.
"""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Типы оборудования (как в info.txt)
EQUIPMENT_TYPE_PIPELINE = 0
EQUIPMENT_TYPE_PUMP = 4
EQUIPMENT_TYPE_COMPRESSOR = 5

# Емкостное оборудование (для него применяем формулу по volume_m3 и fill_fraction)
EQUIPMENT_TYPE_CAPACITIVE = {1, 2, 3, 6, 7}

DEFAULT_PUMP_AMOUNT_T = 0.05
DEFAULT_COMPRESSOR_AMOUNT_T = 0.01


def resolve_db_path() -> Path:
    """Определяем путь к iris.sqlite3 в типовой структуре проекта."""
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "data" / "iris.sqlite3",
        base_dir / "iris.sqlite3",
        Path("data") / "iris.sqlite3",
        Path("iris.sqlite3"),
    ]
    for p in candidates:
        if p.exists():
            return p
    # если БД еще не создана, возвращаем ожидаемый путь
    return base_dir / "data" / "iris.sqlite3"


def safe_json_loads(text: Optional[str]) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def get_densities(physical_json_text: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """Возвращает (density_liquid_kg_per_m3, density_gas_kg_per_m3)."""
    physical = safe_json_loads(physical_json_text)
    rho_l = physical.get("density_liquid_kg_per_m3")
    rho_g = physical.get("density_gas_kg_per_m3")

    try:
        rho_l = float(rho_l) if rho_l is not None else None
    except (TypeError, ValueError):
        rho_l = None

    try:
        rho_g = float(rho_g) if rho_g is not None else None
    except (TypeError, ValueError):
        rho_g = None

    return rho_l, rho_g


def amount_t_capacitive(
    volume_m3: Optional[float],
    fill_fraction: Optional[float],
    rho_l: Optional[float],
    rho_g: Optional[float],
) -> float:
    if volume_m3 is None:
        return 0.0
    try:
        V = float(volume_m3)
    except (TypeError, ValueError):
        return 0.0

    ff = 0.0
    if fill_fraction is not None:
        try:
            ff = float(fill_fraction)
        except (TypeError, ValueError):
            ff = 0.0
    ff = max(0.0, min(1.0, ff))

    m_kg = 0.0
    if rho_l is not None:
        m_kg += V * ff * rho_l
    if rho_g is not None:
        m_kg += V * (1.0 - ff) * rho_g

    return m_kg / 1000.0  # т


def pipeline_internal_volume_m3(
    length_m: Optional[float],
    diameter_mm: Optional[float],
    wall_thickness_mm: Optional[float],
) -> float:
    """Внутренний объем трубы по протяженности и диаметру, исключая толщину стенки."""
    if length_m is None or diameter_mm is None or wall_thickness_mm is None:
        return 0.0

    try:
        L = float(length_m)
        D = float(diameter_mm)
        t = float(wall_thickness_mm)
    except (TypeError, ValueError):
        return 0.0

    d_in_mm = D - 2.0 * t
    if L <= 0 or d_in_mm <= 0:
        return 0.0

    d_in_m = d_in_mm / 1000.0
    area = math.pi * (d_in_m / 2.0) ** 2
    return area * L


def amount_t_pipeline(
    phase_state: Optional[str],
    volume_m3: float,
    fill_fraction: Optional[float],
    rho_l: Optional[float],
    rho_g: Optional[float],
) -> float:
    ps = (phase_state or "").strip()

    if ps == "ж.ф.":
        return (volume_m3 * (rho_l or 0.0)) / 1000.0
    if ps == "г.ф.":
        return (volume_m3 * (rho_g or 0.0)) / 1000.0

    # "ж.ф.+г.ф." (или другое значение): если есть fill_fraction — применяем емкостную формулу
    if fill_fraction is not None:
        return amount_t_capacitive(volume_m3, fill_fraction, rho_l, rho_g)

    # Фолбэк: используем доступную плотность
    if rho_l is not None and rho_g is None:
        return (volume_m3 * rho_l) / 1000.0
    if rho_g is not None and rho_l is None:
        return (volume_m3 * rho_g) / 1000.0

    # Если обе плотности есть, но fill_fraction нет — считаем, что труба заполнена газовой фазой
    if rho_g is not None:
        return (volume_m3 * rho_g) / 1000.0

    return 0.0


def fill_hazardous_substance_amounts(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")

        # 1) Очистка таблицы
        conn.execute("DELETE FROM hazardous_substance_amounts;")

        # 2) Данные оборудования + физические свойства вещества
        rows = conn.execute(
            """
            SELECT
              e.id AS equipment_id,
              e.substance_id,
              e.equipment_name,
              e.phase_state,
              e.equipment_type,
              e.length_m,
              e.diameter_mm,
              e.wall_thickness_mm,
              e.volume_m3,
              e.fill_fraction,
              e.pressure_mpa,
              e.substance_temperature_c,
              s.physical_json
            FROM equipment e
            JOIN substances s ON s.id = e.substance_id
            ORDER BY e.id;
            """
        ).fetchall()

        payload = []
        for (
            equipment_id,
            substance_id,
            equipment_name,
            phase_state,
            equipment_type,
            length_m,
            diameter_mm,
            wall_thickness_mm,
            volume_m3,
            fill_fraction,
            pressure_mpa,
            substance_temperature_c,
            physical_json_text,
        ) in rows:
            rho_l, rho_g = get_densities(physical_json_text)

            if equipment_type == EQUIPMENT_TYPE_PUMP:
                amount_t = DEFAULT_PUMP_AMOUNT_T
            elif equipment_type == EQUIPMENT_TYPE_COMPRESSOR:
                amount_t = DEFAULT_COMPRESSOR_AMOUNT_T
            elif equipment_type == EQUIPMENT_TYPE_PIPELINE:
                V = pipeline_internal_volume_m3(length_m, diameter_mm, wall_thickness_mm)
                amount_t = amount_t_pipeline(phase_state, V, fill_fraction, rho_l, rho_g)
            else:
                # емкостное и прочее (если указаны volume_m3 / fill_fraction)
                amount_t = amount_t_capacitive(volume_m3, fill_fraction, rho_l, rho_g)

            if amount_t < 0:
                amount_t = 0.0

            # округление массы и давления
            amount_t = round(amount_t, 3)

            pressure_mpa_rounded = None
            if pressure_mpa is not None:
                try:
                    pressure_mpa_rounded = round(float(pressure_mpa), 2)
                except (TypeError, ValueError):
                    pressure_mpa_rounded = None

            payload.append(
                {
                    "substance_id": substance_id,
                    "equipment_id": equipment_id,
                    "equipment_name": equipment_name,
                    "amount_t": amount_t,
                    "phase_state": phase_state,
                    "pressure_mpa": pressure_mpa_rounded,
                    "substance_temperature_c": substance_temperature_c,
                }
            )

        # 3) Вставка результатов
        conn.executemany(
            """
            INSERT INTO hazardous_substance_amounts (
              substance_id, equipment_id, equipment_name, amount_t,
              phase_state, pressure_mpa, substance_temperature_c
            ) VALUES (
              :substance_id, :equipment_id, :equipment_name, :amount_t,
              :phase_state, :pressure_mpa, :substance_temperature_c
            );
            """,
            payload,
        )

        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM hazardous_substance_amounts;").fetchone()[0]
        print(f"OK: hazardous_substance_amounts заполнена. Записей: {count}")
    finally:
        conn.close()


def main() -> None:
    db_path = resolve_db_path()
    fill_hazardous_substance_amounts(db_path)


if __name__ == "__main__":
    main()
