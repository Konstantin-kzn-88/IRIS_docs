# Включение/отключение отладочного вывода
DEBUG = False  # True -> печатаем отладку, False -> молчим


def calculate_people_damage(
        sc_line: int,
        equipment_type: int,
        kind: int,
        possible_dead: int,
        possible_injured: int,
):
    result = {}
    result["fatalities_count"] = None
    result["injured_count"] = None

    if equipment_type == 0:
        if kind == 0:
            if sc_line in (1,):  # пожар
                result["fatalities_count"] = max(0, possible_dead - 1)
                result["injured_count"] = max(0, possible_injured - 1)
            elif sc_line in (2,):  # взрыв
                result["fatalities_count"] = possible_dead
                result["injured_count"] = possible_injured
            elif sc_line in (3, 6):  # ликвидация
                result["fatalities_count"] = 0
                result["injured_count"] = 0
            elif sc_line in (4, 5):  # вспышка и пожар частичный
                result["fatalities_count"] = 0
                result["injured_count"] = 1

            if DEBUG:
                print("Погибшие/раненые", result["fatalities_count"], result["injured_count"])
                print(20 * "-")

            return result

    else:
        return result
