# main.py

# -------- substances --------
from models.substance import (
    init_db as init_substances_db,
    seed_default_substances_if_empty,
    list_substances,
)

# -------- equipment --------
from models.equipment import (
    init_db as init_equipment_db,
    seed_equipment_for_default_substances_if_empty,
    list_equipment,
)

# -------- calculations --------
from models.calculations import recalc_hazardous_amounts


def main():
    # 1. Создаём вещества
    init_substances_db()


    substances = list_substances()
    print(f"Веществ создано: {len(substances)}")

    # 2. Создаём оборудование
    init_equipment_db()


    equipment = list_equipment()
    print(f"Оборудования создано: {len(equipment)}")

    # 3. Расчёт количества опасного вещества
    recalc_hazardous_amounts()
    print("Расчёт количества опасного вещества выполнен")

    print("Готово. Проверьте таблицу hazardous_amounts в БД.")


if __name__ == "__main__":
    main()
