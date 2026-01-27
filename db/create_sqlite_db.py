import json
import sqlite3

from core.path import DB_PATH, SCHEMA_PATH, SUBSTANCES_JSON, EQUIPMENT_JSON


def to_json_text(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def get_nested(dct, *path, default=None):
    cur = dct
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def main():
    substances = json.loads(SUBSTANCES_JSON.read_text(encoding="utf-8"))
    equipment = json.loads(EQUIPMENT_JSON.read_text(encoding="utf-8"))

    if DB_PATH.exists():
        DB_PATH.unlink()

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema_sql)

        # ------------------------------
        # substances
        # ------------------------------
        conn.executemany(
            '''
            INSERT INTO substances (
              id, name, kind, formula,
              composition_json, physical_json, explosion_json, toxicity_json,

              composition_notes, composition_components_json,

              physical_molar_mass_kg_per_mol,
              physical_density_liquid_kg_per_m3,
              physical_density_gas_kg_per_m3,
              physical_evaporation_heat_J_per_kg,
              physical_boiling_point_C,

              explosion_explosion_hazard_class,
              explosion_flash_point_C,
              explosion_lel_percent,
              explosion_autoignition_temp_C,
              explosion_burning_rate_kg_per_s_m2,
              explosion_heat_of_combustion_kJ_per_kg,
              explosion_expansion_degree,
              explosion_energy_reserve_factor,

              toxicity_hazard_class,
              toxicity_pdk_mg_per_m3,
              toxicity_threshold_tox_dose_mg_min_per_L,
              toxicity_lethal_tox_dose_mg_min_per_L,

              reactivity, odor, corrosiveness, precautions, impact,
              protection, neutralization_methods, first_aid
            ) VALUES (
              :id, :name, :kind, :formula,
              :composition_json, :physical_json, :explosion_json, :toxicity_json,

              :composition_notes, :composition_components_json,

              :physical_molar_mass_kg_per_mol,
              :physical_density_liquid_kg_per_m3,
              :physical_density_gas_kg_per_m3,
              :physical_evaporation_heat_J_per_kg,
              :physical_boiling_point_C,

              :explosion_explosion_hazard_class,
              :explosion_flash_point_C,
              :explosion_lel_percent,
              :explosion_autoignition_temp_C,
              :explosion_burning_rate_kg_per_s_m2,
              :explosion_heat_of_combustion_kJ_per_kg,
              :explosion_expansion_degree,
              :explosion_energy_reserve_factor,

              :toxicity_hazard_class,
              :toxicity_pdk_mg_per_m3,
              :toxicity_threshold_tox_dose_mg_min_per_L,
              :toxicity_lethal_tox_dose_mg_min_per_L,

              :reactivity, :odor, :corrosiveness, :precautions, :impact,
              :protection, :neutralization_methods, :first_aid
            );
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

                    # распакованные поля composition
                    "composition_notes": get_nested(s, "composition", "notes"),
                    "composition_components_json": to_json_text(get_nested(s, "composition", "components")),

                    # распакованные поля physical
                    "physical_molar_mass_kg_per_mol": get_nested(s, "physical", "molar_mass_kg_per_mol"),
                    "physical_density_liquid_kg_per_m3": get_nested(s, "physical", "density_liquid_kg_per_m3"),
                    "physical_density_gas_kg_per_m3": get_nested(s, "physical", "density_gas_kg_per_m3"),
                    "physical_evaporation_heat_J_per_kg": get_nested(s, "physical", "evaporation_heat_J_per_kg"),
                    "physical_boiling_point_C": get_nested(s, "physical", "boiling_point_C"),

                    # распакованные поля explosion
                    "explosion_explosion_hazard_class": get_nested(s, "explosion", "explosion_hazard_class"),
                    "explosion_flash_point_C": get_nested(s, "explosion", "flash_point_C"),
                    "explosion_lel_percent": get_nested(s, "explosion", "lel_percent"),
                    "explosion_autoignition_temp_C": get_nested(s, "explosion", "autoignition_temp_C"),
                    "explosion_burning_rate_kg_per_s_m2": get_nested(s, "explosion", "burning_rate_kg_per_s_m2"),
                    "explosion_heat_of_combustion_kJ_per_kg": get_nested(s, "explosion", "heat_of_combustion_kJ_per_kg"),
                    "explosion_expansion_degree": get_nested(s, "explosion", "expansion_degree"),
                    "explosion_energy_reserve_factor": get_nested(s, "explosion", "energy_reserve_factor"),

                    # распакованные поля toxicity
                    "toxicity_hazard_class": get_nested(s, "toxicity", "hazard_class"),
                    "toxicity_pdk_mg_per_m3": get_nested(s, "toxicity", "pdk_mg_per_m3"),
                    "toxicity_threshold_tox_dose_mg_min_per_L": get_nested(s, "toxicity", "threshold_tox_dose_mg_min_per_L"),
                    "toxicity_lethal_tox_dose_mg_min_per_L": get_nested(s, "toxicity", "lethal_tox_dose_mg_min_per_L"),

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

        # ------------------------------
        # equipment
        # ------------------------------
        conn.executemany(
            '''
            INSERT INTO equipment (
              id, substance_id, equipment_name, quantity_equipment,
              hazard_component, clutter_degree, phase_state,
              coord_type, equipment_type, coordinates_json,
              length_m, diameter_mm, wall_thickness_mm,
              volume_m3, fill_fraction, pressure_mpa,
              spill_coefficient, spill_area_m2,
              substance_temperature_c,
              shutdown_time_s, evaporation_time_s,
              possible_dead, possible_injured
            ) VALUES (
              :id, :substance_id, :equipment_name, :quantity_equipment,
              :hazard_component, :clutter_degree, :phase_state,
              :coord_type, :equipment_type, :coordinates_json,
              :length_m, :diameter_mm, :wall_thickness_mm,
              :volume_m3, :fill_fraction, :pressure_mpa,
              :spill_coefficient, :spill_area_m2,
              :substance_temperature_c,
              :shutdown_time_s, :evaporation_time_s,
              :possible_dead, :possible_injured
            );
            ''',
            [
                {
                    "id": e.get("id"),
                    "substance_id": e.get("substance_id"),
                    "equipment_name": e.get("equipment_name"),
                    "quantity_equipment": e.get("quantity_equipment", 1),
                    "hazard_component": e.get("hazard_component"),
                    "clutter_degree": e.get("clutter_degree"),
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

                    # новые поля (если отсутствуют в JSON — будут 0)
                    "possible_dead": e.get("possible_dead", 0),
                    "possible_injured": e.get("possible_injured", 0),
                }
                for e in equipment
            ],
        )

        conn.commit()
        print("OK: база данных пересоздана")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
