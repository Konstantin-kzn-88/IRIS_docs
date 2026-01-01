PRAGMA foreign_keys = ON;

-- =========================================================
-- 1) Вещества
-- =========================================================
CREATE TABLE IF NOT EXISTS substances (
  id                         INTEGER PRIMARY KEY,
  name                       TEXT    NOT NULL,
  kind                       INTEGER NOT NULL,
  formula                    TEXT,

  composition_json           TEXT,   -- JSON
  physical_json              TEXT,   -- JSON
  explosion_json             TEXT,   -- JSON
  toxicity_json              TEXT,   -- JSON

  -- Распакованные поля из JSON (для удобства запросов)
  composition_notes            TEXT,
  composition_components_json  TEXT,   -- JSON
  physical_molar_mass_kg_per_mol REAL,
  physical_density_liquid_kg_per_m3 REAL,
  physical_density_gas_kg_per_m3 REAL,
  physical_evaporation_heat_J_per_kg REAL,
  physical_boiling_point_C     REAL,
  explosion_explosion_hazard_class INTEGER,
  explosion_flash_point_C      REAL,
  explosion_lel_percent        REAL,
  explosion_autoignition_temp_C REAL,
  explosion_burning_rate_kg_per_s_m2 REAL,
  explosion_heat_of_combustion_kJ_per_kg REAL,
  explosion_expansion_degree   REAL,
  explosion_energy_reserve_factor REAL,
  toxicity_hazard_class        INTEGER,
  toxicity_pdk_mg_per_m3       REAL,
  toxicity_threshold_tox_dose_mg_min_per_L REAL,
  toxicity_lethal_tox_dose_mg_min_per_L REAL,


  reactivity                 TEXT,
  odor                       TEXT,
  corrosiveness              TEXT,
  precautions                TEXT,
  impact                     TEXT,
  protection                 TEXT,
  neutralization_methods     TEXT,
  first_aid                  TEXT);

-- =========================================================
-- 2) Оборудование
-- =========================================================
CREATE TABLE IF NOT EXISTS equipment (
    id                      INTEGER PRIMARY KEY,
    substance_id            INTEGER NOT NULL,
    equipment_name          TEXT NOT NULL,

    -- Составляющая опасного объекта
    hazard_component        TEXT NOT NULL,

    -- Степень загроможденности:
    -- 1 — очень загроможденное пространство
    -- 4 — слабо загроможденное пространство
    clutter_degree          INTEGER NOT NULL
                             CHECK (clutter_degree BETWEEN 1 AND 4),

    phase_state             TEXT,
    coord_type              INTEGER,
    equipment_type          INTEGER,
    coordinates_json        TEXT,

    length_m                REAL,
    diameter_mm             REAL,
    wall_thickness_mm       REAL,
    volume_m3               REAL,
    fill_fraction           REAL,
    pressure_mpa            REAL,
    spill_coefficient       REAL,
    spill_area_m2           REAL,
    substance_temperature_c REAL,
    shutdown_time_s         REAL,
    evaporation_time_s      REAL,

    FOREIGN KEY (substance_id) REFERENCES substances(id)
);

CREATE INDEX IF NOT EXISTS idx_equipment_substance_id
  ON equipment(substance_id);

-- =========================================================
-- 4) Расчеты
-- =========================================================
CREATE TABLE IF NOT EXISTS calculations (
  id                         INTEGER PRIMARY KEY,

  equipment_id               INTEGER NOT NULL,
  equipment_name             TEXT    NOT NULL,

  -- Составляющая опасного объекта, для которой рассчитан сценарий
  hazard_component           TEXT    NOT NULL,

  -- Сквозная нумерация сценариев по всей таблице calculations
  scenario_no                INTEGER NOT NULL UNIQUE,

  base_frequency             REAL,   -- базовая частота
  accident_event_probability REAL,   -- вероятность события аварии
  scenario_frequency         REAL,   -- частота сценария аварии

  amount_t                   REAL    NOT NULL,  -- количество ОВ, т

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

CREATE INDEX IF NOT EXISTS idx_calc_equipment_id
  ON calculations(equipment_id);

CREATE INDEX IF NOT EXISTS idx_calc_hazard_component
  ON calculations(hazard_component);
