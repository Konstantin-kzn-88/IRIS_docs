import json
import sqlite3
from pathlib import Path

DB_PATH = Path("iris.sqlite3")
SUBSTANCES_JSON = Path("../../../Users/Konstantin/OneDrive/Рабочий стол/substances.json")
EQUIPMENT_JSON = Path("../../../Users/Konstantin/OneDrive/Рабочий стол/equipment.json")

SCHEMA_SQL = r'''
PRAGMA foreign_keys = ON;

-- 1) Вещества (поля из JSON; вложенные объекты храним как JSON-текст)
CREATE TABLE IF NOT EXISTS substances (
  id                         INTEGER PRIMARY KEY,
  name                       TEXT    NOT NULL,
  kind                       INTEGER NOT NULL,
  formula                    TEXT,

  composition_json           TEXT,   -- JSON
  physical_json              TEXT,   -- JSON
  explosion_json             TEXT,   -- JSON
  toxicity_json              TEXT,   -- JSON

  reactivity                 TEXT,
  odor                       TEXT,
  corrosiveness              TEXT,
  precautions                TEXT,
  impact                     TEXT,
  protection                 TEXT,
  neutralization_methods     TEXT,
  first_aid                  TEXT
);

-- 2) Оборудование (поля из JSON; coordinates храним как JSON-текст)
CREATE TABLE IF NOT EXISTS equipment (
  id                         INTEGER PRIMARY KEY,
  substance_id               INTEGER NOT NULL,
  equipment_name             TEXT    NOT NULL,
  phase_state                TEXT,
  coord_type                 INTEGER,
  equipment_type             INTEGER,
  coordinates_json           TEXT,   -- JSON

  length_m                   REAL,
  diameter_mm                REAL,
  wall_thickness_mm          REAL,
  volume_m3                  REAL,
  fill_fraction              REAL,
  pressure_mpa               REAL,
  spill_coefficient          REAL,
  spill_area_m2              REAL,
  substance_temperature_c    REAL,
  shutdown_time_s            REAL,
  evaporation_time_s         REAL,

  FOREIGN KEY (substance_id) REFERENCES substances(id)
);

CREATE INDEX IF NOT EXISTS idx_equipment_substance_id ON equipment(substance_id);

-- 3) Количество опасного вещества
CREATE TABLE IF NOT EXISTS hazardous_substance_amounts (
  id                         INTEGER PRIMARY KEY,
  substance_id               INTEGER NOT NULL,
  equipment_id               INTEGER NOT NULL,

  equipment_name             TEXT    NOT NULL,  -- денормализация для удобства отчетности
  amount_t                   REAL    NOT NULL,  -- количество ОВ, т

  phase_state                TEXT,
  pressure_mpa               REAL,
  substance_temperature_c    REAL,

  FOREIGN KEY (substance_id) REFERENCES substances(id),
  FOREIGN KEY (equipment_id) REFERENCES equipment(id)
);

CREATE INDEX IF NOT EXISTS idx_hsa_substance_id ON hazardous_substance_amounts(substance_id);
CREATE INDEX IF NOT EXISTS idx_hsa_equipment_id ON hazardous_substance_amounts(equipment_id);

-- 4) Расчеты
CREATE TABLE IF NOT EXISTS calculations (
  id                         INTEGER PRIMARY KEY,
  equipment_id               INTEGER NOT NULL,
  equipment_name             TEXT    NOT NULL,

  base_frequency             REAL,   -- базовая частота
  accident_event_probability REAL,   -- вероятность события аварии
  scenario_frequency         REAL,   -- частота сценария аварии

  ov_in_accident_t           REAL,   -- количество ОВ участвующего в аварии (т)
  ov_in_hazard_factor_t      REAL,   -- количество ОВ в создании поражающего фактора (т)

  q_10_5                     REAL,
  q_7_0                      REAL,
  q_4_2                      REAL,
  q_1_4                      REAL,

  p_70                       REAL,
  p_28                       REAL,
  p_14                       REAL,
  p_5                        REAL,
  p_2                        REAL,

  l_f                        REAL,
  d_f                        REAL,
  r_nkpr                     REAL,
  r_vsp                      REAL,
  l_pt                       REAL,
  p_pt                       REAL,

  q_600                      REAL,
  q_320                      REAL,
  q_220                      REAL,
  q_120                      REAL,

  s_t                        REAL,

  fatalities_count           INTEGER, -- кол-во пог.
  injured_count              INTEGER, -- кол-во постр.

  direct_losses              REAL,   -- прямые потери
  liquidation_costs          REAL,   -- затраты на ликвидацию
  social_losses              REAL,   -- социальные потери
  indirect_damage            REAL,   -- косвенный ущерб
  total_environmental_damage REAL,   -- суммарный экологический ущерб
  total_damage               REAL,   -- суммарный ущерб

  collective_risk_fatalities REAL,   -- кол. риск погибшие
  collective_risk_injured    REAL,   -- кол. риск пострадавшие
  expected_value             REAL,   -- мат. ожидание

  individual_risk_fatalities REAL,   -- инд. риск погибшие
  individual_risk_injured    REAL,   -- инд. риск пострадавшие

  FOREIGN KEY (equipment_id) REFERENCES equipment(id)
);

CREATE INDEX IF NOT EXISTS idx_calc_equipment_id ON calculations(equipment_id);
'''

def to_json_text(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)

def main():
    # Read JSON
    substances = json.loads(SUBSTANCES_JSON.read_text(encoding="utf-8"))
    equipment = json.loads(EQUIPMENT_JSON.read_text(encoding="utf-8"))

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_SQL)

        # Upsert substances
        conn.executemany(
            '''
            INSERT INTO substances (
              id, name, kind, formula,
              composition_json, physical_json, explosion_json, toxicity_json,
              reactivity, odor, corrosiveness, precautions, impact,
              protection, neutralization_methods, first_aid
            ) VALUES (
              :id, :name, :kind, :formula,
              :composition_json, :physical_json, :explosion_json, :toxicity_json,
              :reactivity, :odor, :corrosiveness, :precautions, :impact,
              :protection, :neutralization_methods, :first_aid
            )
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              kind=excluded.kind,
              formula=excluded.formula,
              composition_json=excluded.composition_json,
              physical_json=excluded.physical_json,
              explosion_json=excluded.explosion_json,
              toxicity_json=excluded.toxicity_json,
              reactivity=excluded.reactivity,
              odor=excluded.odor,
              corrosiveness=excluded.corrosiveness,
              precautions=excluded.precautions,
              impact=excluded.impact,
              protection=excluded.protection,
              neutralization_methods=excluded.neutralization_methods,
              first_aid=excluded.first_aid;
            ''',
            [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "kind": s.get("kind"),
                    "formula": s.get("formula"),
                    "composition_json": to_json_text(s.get("composition")),
                    "physical_json": to_json_text(s.get("physical")),
                    "explosion_json": to_json_text(s.get("explosion")),
                    "toxicity_json": to_json_text(s.get("toxicity")),
                    "reactivity": s.get("reactivity"),
                    "odor": s.get("odor"),
                    "corrosiveness": s.get("corrosiveness"),
                    "precautions": s.get("precautions"),
                    "impact": s.get("impact"),
                    "protection": s.get("protection"),
                    "neutralization_methods": s.get("neutralization_methods"),
                    "first_aid": s.get("first_aid"),
                }
                for s in substances
            ],
        )

        # Upsert equipment
        conn.executemany(
            '''
            INSERT INTO equipment (
              id, substance_id, equipment_name, phase_state, coord_type, equipment_type,
              coordinates_json, length_m, diameter_mm, wall_thickness_mm, volume_m3,
              fill_fraction, pressure_mpa, spill_coefficient, spill_area_m2,
              substance_temperature_c, shutdown_time_s, evaporation_time_s
            ) VALUES (
              :id, :substance_id, :equipment_name, :phase_state, :coord_type, :equipment_type,
              :coordinates_json, :length_m, :diameter_mm, :wall_thickness_mm, :volume_m3,
              :fill_fraction, :pressure_mpa, :spill_coefficient, :spill_area_m2,
              :substance_temperature_c, :shutdown_time_s, :evaporation_time_s
            )
            ON CONFLICT(id) DO UPDATE SET
              substance_id=excluded.substance_id,
              equipment_name=excluded.equipment_name,
              phase_state=excluded.phase_state,
              coord_type=excluded.coord_type,
              equipment_type=excluded.equipment_type,
              coordinates_json=excluded.coordinates_json,
              length_m=excluded.length_m,
              diameter_mm=excluded.diameter_mm,
              wall_thickness_mm=excluded.wall_thickness_mm,
              volume_m3=excluded.volume_m3,
              fill_fraction=excluded.fill_fraction,
              pressure_mpa=excluded.pressure_mpa,
              spill_coefficient=excluded.spill_coefficient,
              spill_area_m2=excluded.spill_area_m2,
              substance_temperature_c=excluded.substance_temperature_c,
              shutdown_time_s=excluded.shutdown_time_s,
              evaporation_time_s=excluded.evaporation_time_s;
            ''',
            [
                {
                    "id": e.get("id"),
                    "substance_id": e.get("substance_id"),
                    "equipment_name": e.get("equipment_name"),
                    "phase_state": e.get("phase_state"),
                    "coord_type": e.get("coord_type"),
                    "equipment_type": e.get("equipment_type"),
                    "coordinates_json": to_json_text(e.get("coordinates")),
                    "length_m": e.get("length_m"),
                    "diameter_mm": e.get("diameter_mm"),
                    "wall_thickness_mm": e.get("wall_thickness_mm"),
                    "volume_m3": e.get("volume_m3"),
                    "fill_fraction": e.get("fill_fraction"),
                    "pressure_mpa": e.get("pressure_mpa"),
                    "spill_coefficient": e.get("spill_coefficient"),
                    "spill_area_m2": e.get("spill_area_m2"),
                    "substance_temperature_c": e.get("substance_temperature_c"),
                    "shutdown_time_s": e.get("shutdown_time_s"),
                    "evaporation_time_s": e.get("evaporation_time_s"),
                }
                for e in equipment
            ],
        )

        conn.commit()
        print(f"OK: создана БД {DB_PATH.resolve()}")
        print(f"substances: {conn.execute('SELECT COUNT(*) FROM substances').fetchone()[0]}")
        print(f"equipment:  {conn.execute('SELECT COUNT(*) FROM equipment').fetchone()[0]}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
