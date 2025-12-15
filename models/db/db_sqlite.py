# db_sqlite.py
import sqlite3
import json
from typing import Optional, Any, Dict, List, Tuple

from models.substance.substance import Substance
from models.equipment.equipment_entities import TechPipeline, PumpCompressorEquipment, VesselApparatusEquipment


def _jdump(x: Any) -> Optional[str]:
    return None if x is None else json.dumps(x, ensure_ascii=False)

def _jload(s: Optional[str]) -> Any:
    return None if s is None else json.loads(s)


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS substances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        kind INTEGER NOT NULL,
        formula TEXT NOT NULL DEFAULT '',
        composition_json TEXT,
        physical_json TEXT,
        explosion_json TEXT,
        toxicity_json TEXT,
        reactivity TEXT NOT NULL DEFAULT '',
        odor TEXT NOT NULL DEFAULT '',
        corrosiveness TEXT NOT NULL DEFAULT '',
        precautions TEXT NOT NULL DEFAULT '',
        impact TEXT NOT NULL DEFAULT '',
        protection TEXT NOT NULL DEFAULT '',
        neutralization_methods TEXT NOT NULL DEFAULT '',
        first_aid TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_class TEXT NOT NULL,

        substance_id INTEGER NOT NULL,
        coord_type INTEGER NOT NULL,
        coords_json TEXT,

        pressure_mpa REAL NOT NULL,
        phase_state TEXT NOT NULL,
        spill_coefficient REAL NOT NULL,
        spill_area_m2 REAL NOT NULL,
        substance_temperature_c REAL NOT NULL,
        shutdown_time_s REAL NOT NULL,
        evaporation_time_s REAL NOT NULL,

        -- TechPipeline
        length_m REAL,
        diameter_mm REAL,
        wall_thickness_mm REAL,
        base_frequency_rupture_per_year REAL,
        base_frequency_depressurization_per_year REAL,

        -- PumpCompressorEquipment
        pce_equipment_type INTEGER,
        pipeline_diameter_mm REAL,
        base_frequency_catastrophic_per_year REAL,
        base_frequency_leak_per_year REAL,

        -- VesselApparatusEquipment
        vae_equipment_type INTEGER,
        volume_m3 REAL,
        fill_fraction REAL,
        base_frequency_full_failure_per_year REAL,
        vae_base_frequency_leak_per_year REAL,

        FOREIGN KEY (substance_id) REFERENCES substances(id) ON DELETE RESTRICT
    );
    """)
    conn.commit()


# -------------------- CRUD: Substance --------------------

def create_substance(conn: sqlite3.Connection, s: Substance) -> int:
    cur = conn.execute("""
        INSERT INTO substances (
            name, kind, formula,
            composition_json, physical_json, explosion_json, toxicity_json,
            reactivity, odor, corrosiveness, precautions, impact, protection,
            neutralization_methods, first_aid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        s.name, s.kind, s.formula,
        _jdump(s.composition), _jdump(s.physical), _jdump(s.explosion), _jdump(s.toxicity),
        s.reactivity, s.odor, s.corrosiveness, s.precautions, s.impact, s.protection,
        s.neutralization_methods, s.first_aid
    ))
    conn.commit()
    return int(cur.lastrowid)


def get_substance(conn: sqlite3.Connection, substance_id: int) -> Optional[Substance]:
    row = conn.execute("SELECT * FROM substances WHERE id = ?", (substance_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    return Substance(
        id=d["id"],
        name=d["name"],
        kind=d["kind"],
        formula=d["formula"],
        composition=_jload(d["composition_json"]),
        physical=_jload(d["physical_json"]),
        explosion=_jload(d["explosion_json"]),
        toxicity=_jload(d["toxicity_json"]),
        reactivity=d["reactivity"],
        odor=d["odor"],
        corrosiveness=d["corrosiveness"],
        precautions=d["precautions"],
        impact=d["impact"],
        protection=d["protection"],
        neutralization_methods=d["neutralization_methods"],
        first_aid=d["first_aid"],
    )


def update_substance(conn: sqlite3.Connection, s: Substance) -> None:
    if s.id is None:
        raise ValueError("Substance.id обязателен для update")

    conn.execute("""
        UPDATE substances SET
            name = ?, kind = ?, formula = ?,
            composition_json = ?, physical_json = ?, explosion_json = ?, toxicity_json = ?,
            reactivity = ?, odor = ?, corrosiveness = ?, precautions = ?, impact = ?, protection = ?,
            neutralization_methods = ?, first_aid = ?
        WHERE id = ?
    """, (
        s.name, s.kind, s.formula,
        _jdump(s.composition), _jdump(s.physical), _jdump(s.explosion), _jdump(s.toxicity),
        s.reactivity, s.odor, s.corrosiveness, s.precautions, s.impact, s.protection,
        s.neutralization_methods, s.first_aid,
        s.id
    ))
    conn.commit()


def delete_substance(conn: sqlite3.Connection, substance_id: int) -> None:
    # ON DELETE RESTRICT не даст удалить, если есть оборудование
    conn.execute("DELETE FROM substances WHERE id = ?", (substance_id,))
    conn.commit()


def list_substances(conn: sqlite3.Connection) -> List[Substance]:
    rows = conn.execute("SELECT id FROM substances ORDER BY name").fetchall()
    out: List[Substance] = []
    for r in rows:
        s = get_substance(conn, int(r["id"]))
        if s:
            out.append(s)
    return out


# -------------------- CRUD: Equipment --------------------

def create_equipment(conn: sqlite3.Connection, eq: Any) -> int:
    d = eq.to_dict()

    common = (
        d["equipment_class"],
        d["substance_id"],
        d["coord_type"],
        _jdump(d["coords"]),
        d["pressure_mpa"],
        d["phase_state"],
        d["spill_coefficient"],
        d["spill_area_m2"],
        d["substance_temperature_c"],
        d["shutdown_time_s"],
        d["evaporation_time_s"],
    )

    if d["equipment_class"] == "TechPipeline":
        cur = conn.execute("""
            INSERT INTO equipment (
                equipment_class, substance_id, coord_type, coords_json,
                pressure_mpa, phase_state, spill_coefficient, spill_area_m2,
                substance_temperature_c, shutdown_time_s, evaporation_time_s,

                length_m, diameter_mm, wall_thickness_mm,
                base_frequency_rupture_per_year, base_frequency_depressurization_per_year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, common + (
            d["length_m"], d["diameter_mm"], d["wall_thickness_mm"],
            d["base_frequency_rupture_per_year"], d["base_frequency_depressurization_per_year"]
        ))

    elif d["equipment_class"] == "PumpCompressorEquipment":
        cur = conn.execute("""
            INSERT INTO equipment (
                equipment_class, substance_id, coord_type, coords_json,
                pressure_mpa, phase_state, spill_coefficient, spill_area_m2,
                substance_temperature_c, shutdown_time_s, evaporation_time_s,

                pce_equipment_type, pipeline_diameter_mm,
                base_frequency_catastrophic_per_year, base_frequency_leak_per_year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, common + (
            d["equipment_type"], d["pipeline_diameter_mm"],
            d["base_frequency_catastrophic_per_year"], d["base_frequency_leak_per_year"]
        ))

    elif d["equipment_class"] == "VesselApparatusEquipment":
        cur = conn.execute("""
            INSERT INTO equipment (
                equipment_class, substance_id, coord_type, coords_json,
                pressure_mpa, phase_state, spill_coefficient, spill_area_m2,
                substance_temperature_c, shutdown_time_s, evaporation_time_s,

                vae_equipment_type, volume_m3, fill_fraction,
                base_frequency_full_failure_per_year, vae_base_frequency_leak_per_year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, common + (
            d["equipment_type"], d["volume_m3"], d["fill_fraction"],
            d["base_frequency_full_failure_per_year"], d["base_frequency_leak_per_year"]
        ))
    else:
        raise ValueError(f"Неизвестный equipment_class: {d['equipment_class']}")

    conn.commit()
    return int(cur.lastrowid)


def _row_to_equipment(row: sqlite3.Row) -> Any:
    d = dict(row)

    # общие поля
    substance_id = d["substance_id"]
    coord_type = d["coord_type"]
    coords = _jload(d["coords_json"])

    common_kwargs = dict(
        substance_id=substance_id,
        coords=coords,
        coord_type=coord_type,

        pressure_mpa=d["pressure_mpa"],
        phase_state=d["phase_state"],
        spill_coefficient=d["spill_coefficient"],
        spill_area_m2=d["spill_area_m2"],
        substance_temperature_c=d["substance_temperature_c"],
        shutdown_time_s=d["shutdown_time_s"],
        evaporation_time_s=d["evaporation_time_s"],
    )

    if d["equipment_class"] == "TechPipeline":
        return TechPipeline(
            length_m=d["length_m"],
            diameter_mm=d["diameter_mm"],
            wall_thickness_mm=d["wall_thickness_mm"],
            base_frequency_rupture_per_year=d["base_frequency_rupture_per_year"],
            base_frequency_depressurization_per_year=d["base_frequency_depressurization_per_year"],
            **common_kwargs
        )

    if d["equipment_class"] == "PumpCompressorEquipment":
        return PumpCompressorEquipment(
            equipment_type=d["pce_equipment_type"],
            pipeline_diameter_mm=d["pipeline_diameter_mm"],
            base_frequency_catastrophic_per_year=d["base_frequency_catastrophic_per_year"],
            base_frequency_leak_per_year=d["base_frequency_leak_per_year"],
            **common_kwargs
        )

    if d["equipment_class"] == "VesselApparatusEquipment":
        return VesselApparatusEquipment(
            equipment_type=d["vae_equipment_type"],
            volume_m3=d["volume_m3"],
            fill_fraction=d["fill_fraction"],
            base_frequency_full_failure_per_year=d["base_frequency_full_failure_per_year"],
            base_frequency_leak_per_year=d["vae_base_frequency_leak_per_year"],
            **common_kwargs
        )

    raise ValueError(f"Неизвестный equipment_class в БД: {d['equipment_class']}")


def get_equipment(conn: sqlite3.Connection, equipment_id: int) -> Optional[Any]:
    row = conn.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()
    if row is None:
        return None
    return _row_to_equipment(row)


def delete_equipment(conn: sqlite3.Connection, equipment_id: int) -> None:
    conn.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
    conn.commit()


def list_equipment(conn: sqlite3.Connection) -> List[Tuple[int, Any]]:
    rows = conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
    out: List[Tuple[int, Any]] = []
    for r in rows:
        eq_obj = _row_to_equipment(r)
        out.append((int(r["id"]), eq_obj))
    return out


def update_equipment(conn: sqlite3.Connection, equipment_id: int, eq: Any) -> None:
    # проще всего: удалить и вставить заново (сохранить equipment_id нельзя при AUTOINCREMENT),
    # но обычно ID важен. Поэтому ниже — нормальный UPDATE по типу.
    d = eq.to_dict()

    base_sql = """
        UPDATE equipment SET
            equipment_class = ?,
            substance_id = ?,
            coord_type = ?,
            coords_json = ?,

            pressure_mpa = ?,
            phase_state = ?,
            spill_coefficient = ?,
            spill_area_m2 = ?,
            substance_temperature_c = ?,
            shutdown_time_s = ?,
            evaporation_time_s = ?
    """

    base_params = [
        d["equipment_class"],
        d["substance_id"],
        d["coord_type"],
        _jdump(d["coords"]),
        d["pressure_mpa"],
        d["phase_state"],
        d["spill_coefficient"],
        d["spill_area_m2"],
        d["substance_temperature_c"],
        d["shutdown_time_s"],
        d["evaporation_time_s"],
    ]

    if d["equipment_class"] == "TechPipeline":
        sql = base_sql + """,
            length_m = ?,
            diameter_mm = ?,
            wall_thickness_mm = ?,
            base_frequency_rupture_per_year = ?,
            base_frequency_depressurization_per_year = ?,

            -- очистка полей других типов
            pce_equipment_type = NULL, pipeline_diameter_mm = NULL,
            base_frequency_catastrophic_per_year = NULL, base_frequency_leak_per_year = NULL,
            vae_equipment_type = NULL, volume_m3 = NULL, fill_fraction = NULL,
            base_frequency_full_failure_per_year = NULL, vae_base_frequency_leak_per_year = NULL
        WHERE id = ?
        """
        params = base_params + [
            d["length_m"], d["diameter_mm"], d["wall_thickness_mm"],
            d["base_frequency_rupture_per_year"], d["base_frequency_depressurization_per_year"],
            equipment_id
        ]

    elif d["equipment_class"] == "PumpCompressorEquipment":
        sql = base_sql + """,
            pce_equipment_type = ?,
            pipeline_diameter_mm = ?,
            base_frequency_catastrophic_per_year = ?,
            base_frequency_leak_per_year = ?,

            length_m = NULL, diameter_mm = NULL, wall_thickness_mm = NULL,
            base_frequency_rupture_per_year = NULL, base_frequency_depressurization_per_year = NULL,
            vae_equipment_type = NULL, volume_m3 = NULL, fill_fraction = NULL,
            base_frequency_full_failure_per_year = NULL, vae_base_frequency_leak_per_year = NULL
        WHERE id = ?
        """
        params = base_params + [
            d["equipment_type"], d["pipeline_diameter_mm"],
            d["base_frequency_catastrophic_per_year"], d["base_frequency_leak_per_year"],
            equipment_id
        ]

    elif d["equipment_class"] == "VesselApparatusEquipment":
        sql = base_sql + """,
            vae_equipment_type = ?,
            volume_m3 = ?,
            fill_fraction = ?,
            base_frequency_full_failure_per_year = ?,
            vae_base_frequency_leak_per_year = ?,

            length_m = NULL, diameter_mm = NULL, wall_thickness_mm = NULL,
            base_frequency_rupture_per_year = NULL, base_frequency_depressurization_per_year = NULL,
            pce_equipment_type = NULL, pipeline_diameter_mm = NULL,
            base_frequency_catastrophic_per_year = NULL, base_frequency_leak_per_year = NULL
        WHERE id = ?
        """
        params = base_params + [
            d["equipment_type"], d["volume_m3"], d["fill_fraction"],
            d["base_frequency_full_failure_per_year"], d["base_frequency_leak_per_year"],
            equipment_id
        ]
    else:
        raise ValueError(f"Неизвестный equipment_class: {d['equipment_class']}")

    conn.execute(sql, params)
    conn.commit()
