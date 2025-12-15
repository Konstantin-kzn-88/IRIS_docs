from models.db.db_sqlite import connect, init_db, create_substance, create_equipment, get_equipment
from models.substance.substance import Substance
from models.equipment.equipment_entities import TechPipeline

conn = connect("iris.db")
init_db(conn)

s = Substance(name="Бензин", kind=0, formula="C_xH_y")
sid = create_substance(conn, s)

pipe = TechPipeline(
    length_m=120.0, diameter_mm=100.0, wall_thickness_mm=6.0,

    substance_id=sid,
    coords=None,
    coord_type=0,

    pressure_mpa=1.6, phase_state="ж.ф.",
    spill_coefficient=0.8, spill_area_m2=120.0,
    substance_temperature_c=35.0, shutdown_time_s=300.0, evaporation_time_s=5000.0
)

eid = create_equipment(conn, pipe)
loaded = get_equipment(conn, eid)
print(loaded.to_dict())