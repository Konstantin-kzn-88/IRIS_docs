"""
Скрипт загрузки ОДНОГО вещества в SQLite базу.

Идея:
- Файл рассчитан на поочерёдную загрузку разных веществ.
- Для добавления нового вещества меняется ТОЛЬКО функция make_substance().
- Имена переменных универсальные (substance, substance_id и т.д.).

Запуск:
1) Рядом должны лежать:
   - substance.py
   - substances_db.py
   - load_single_substance.py
2) Выполнить:
   python load_single_substance.py
"""

from substance import Substance
import substances_db


def make_substance() -> Substance:
    """
    Сформировать объект вещества.

    ВАЖНО:
    Для загрузки другого вещества:
    - меняется ТОЛЬКО тело этой функции;
    - остальной код трогать не нужно.
    """
    substance = Substance(
        name="Нефть (сырая)",
        kind=0,  # 0 — легковоспламеняющаяся жидкость (ориентировочно)
        formula="Смешанная (углеводороды CxHy)",
        odor="Характерный нефтяной запах",
        reactivity="Стабильна при нормальных условиях; реагирует с сильными окислителями.",
        precautions="Избегать нагрева и открытого огня; обеспечить вентиляцию; не допускать разливов.",
        impact="Опасность пожара; загрязнение почвы и воды при разливе.",
        protection="Защитные перчатки, очки; при парах — респиратор.",
        neutralization_methods="Ограждение зоны, сорбенты, сбор загрязнённого материала в тару.",
        first_aid="Кожа — промыть водой с мылом; глаза — промывать 10–15 мин; при вдыхании — свежий воздух.",
    )

    # -----------------------------
    # Состав (примерно)
    # -----------------------------
    substance.composition["main_components"] = (
        "Алканы, циклоалканы, ароматические углеводороды"
    )
    substance.composition["impurities"] = (
        "Сераорганические соединения, смолы, асфальтены (следы)"
    )

    # -----------------------------
    # Физические свойства (примерные)
    # -----------------------------
    substance.physical["molecular_mass_kg_per_mol"] = 0.200  # условное среднее
    substance.physical["density_liquid_kg_per_m3"] = 850.0
    substance.physical["density_gas_kg_per_m3"] = 0.0  # не применяется
    substance.physical["boiling_point_C"] = 200.0  # условный диапазон
    substance.physical["evaporation_heat_J_per_kg"] = 250_000.0

    # -----------------------------
    # Пожаро- и взрывоопасность
    # -----------------------------
    substance.explosion["flash_point_C"] = 60.0
    substance.explosion["lel_percent"] = 1.0
    substance.explosion["autoignition_temp_C"] = 250.0

    # -----------------------------
    # Токсикологические свойства
    # -----------------------------
    substance.toxicity["hazard_class"] = 3
    substance.toxicity["notes"] = (
        "Пары и аэрозоли раздражают дыхательные пути; опасна для экосистем при разливе."
    )

    return substance


def main() -> None:
    """
    Универсальный код загрузки вещества в БД.
    Менять этот код не нужно.
    """
    # Путь к базе данных (по умолчанию из substances_db.py)
    db_path = substances_db.DEFAULT_DB_PATH

    # Подключение к БД и инициализация таблицы
    connection = substances_db.connect(db_path)
    substances_db.init_db(connection)

    # Формируем вещество
    substance = make_substance()

    # Записываем вещество в базу
    substance_id = substances_db.create_substance(connection, substance)

    print("Вещество загружено в базу данных:")
    print(f"  id = {substance_id}")
    print(f"  name = {substance.name}")
    print(f"  kind = {substance.kind} ({substance.kind_name()})")

    # Закрываем соединение
    connection.close()


if __name__ == "__main__":
    main()
