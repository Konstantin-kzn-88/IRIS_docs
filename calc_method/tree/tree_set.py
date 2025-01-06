# Модуль работы с деревьями событий
# @version: 1.0
# @date: 2024-08-29
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# @author: Kuznetsov Konstantin, kuznetsov@yandex.ru
# (C) 2024
# ------------------------------------------------------------------------------------


# Типы веществ (sub_type)
# 0: ЛВЖ (Легковоспламеняющаяся жидкость)
# 1: ЛВЖ токсичная
# 2: СУГ (Сжиженный углеводородный газ)
# 3: СУГ токсичный
# 4: ГЖ (Горючая жидкость)
# 5: ГГ (Горючий газ)
# 6: ГГ токсичный
# 7: Химически опасное вещество (ХОВ) без токсичного облака

# Структура: equipment_type -> substance_type -> (partial_depressurization, full_depressurization)
# Где partial_depressurization и full_depressurization - кортежи ((...вероятность событий...)(...методы расчета...))

equipment_substance_mapping = {
    'Technological_devices': {
        0: {  # ЛВЖ
            'partial': (
                (0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'no_factors', 'gas_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.19, 0.76), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'toxi', 'gas_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.19, 0.76), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ
            'partial': (
                (0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'no_factors', 'gas_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.19, 0.76), ('fire_ball', 'explosion', 'no_factors')),
        },
        3: {  # СУГ токсичный
            'partial': ((0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'toxi', 'gas_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.19, 0.76), ('fire_ball', 'explosion', 'toxi')),
        },
        4: {  # ГЖ
            'partial': ((0.1, 0.045, 0.855), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.1, 0.045, 0.855), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial': ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'no_factors')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('fire_ball', 'explosion', 'flash', 'no_factors')),
        },
        6: {  # ГГ токсичный
            'partial': ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'toxi')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('fire_ball', 'explosion', 'flash', 'toxi')),
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Tank': {
        0: {  # ЛВЖ
            'partial': ((0.1, 0.0450, 0.8550), ('strait_fire', 'flash', 'no_factors')),
            'full': ((0.1, 0.18, 0.72), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.1, 0.0450, 0.8550), ('strait_fire', 'flash', 'toxi')),
            'full': ((0.1, 0.18, 0.72), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ (не может хранится в резервуаре без давления)
            'partial': None,
            'full': None
        },
        3: {  # СУГ токсичный
            'partial': None,
            'full': None
        },
        4: {  # ГЖ
            'partial': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial': None,
            'full': None
        },
        6: {  # ГГ токсичный
            'partial': None,
            'full': None
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Pump': {
        0: {  # ЛВЖ
            'partial': ((0.05, 0.0475, 0.9025), ('liguid_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.05, 0.0475, 0.9025), ('liguid_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ
            'partial': ((0.05, 0.0475, 0.9025), ('liguid_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'explosion', 'no_factors')),
        },
        3: {  # СУГ токсичный
            'partial': ((0.05, 0.0475, 0.9025), ('liguid_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'explosion', 'toxi')),
        },
        4: {  # ГЖ
            'partial': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial': None,
            'full': None
        },
        6: {  # ГГ токсичный
            'partial': None,
            'full': None
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Truck_tank_without_pressure': {
        0: {  # ЛВЖ
            'partial': ((0.1, 0.0450, 0.8550), ('strait_fire', 'flash', 'no_factors')),
            'full': ((0.1, 0.18, 0.72), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.1, 0.0450, 0.8550), ('strait_fire', 'flash', 'toxi')),
            'full': ((0.1, 0.18, 0.72), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ (не может хранится в резервуаре без давления)
            'partial': None,
            'full': None
        },
        3: {  # СУГ токсичный
            'partial': None,
            'full': None
        },
        4: {  # ГЖ
            'partial': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.05, 0.0475, 0.9025), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial': None,
            'full': None
        },
        6: {  # ГГ токсичный
            'partial': None,
            'full': None
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Truck_tank_with_pressure': {
        0: {  # ЛВЖ
            'partial': (
                (0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'no_factors', 'gas_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.19, 0.76), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'toxi', 'gas_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.19, 0.76), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ
            'partial': (
                (0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'no_factors', 'gas_jet', 'flash', 'no_factors')),
            'full': ((0.05, 0.19, 0.76), ('fire_ball', 'explosion', 'no_factors')),
        },
        3: {  # СУГ токсичный
            'partial': ((0.04, 0.16, 0.04, 0.152, 0.608), ('liguid_jet', 'toxi', 'gas_jet', 'flash', 'toxi')),
            'full': ((0.05, 0.19, 0.76), ('fire_ball', 'explosion', 'toxi')),
        },
        4: {  # ГЖ
            'partial': ((0.1, 0.045, 0.855), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.1, 0.045, 0.855), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial': ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'no_factors')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('fire_ball', 'explosion', 'flash', 'no_factors')),
        },
        6: {  # ГГ токсичный
            'partial': ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'toxi')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('fire_ball', 'explosion', 'flash', 'toxi')),
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Pipeline': {
        0: {  # ЛВЖ
            'partial': ((0.2, 0.04, 0.76), ('strait_fire', 'flash', 'no_factors')),
            'full': ((0.2, 0.04, 0.76), ('strait_fire', 'explosion', 'no_factors')),
        },
        1: {  # ЛВЖ токсичная
            'partial': ((0.2, 0.04, 0.76), ('strait_fire', 'flash', 'toxi')),
            'full': ((0.2, 0.04, 0.76), ('strait_fire', 'explosion', 'toxi')),
        },
        2: {  # СУГ
            'partial': (
                (0.0350, 0.0083, 0.0264, 0.9303), ('liguid_jet', 'explosion', 'flash', 'no_factors')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('liguid_jet', 'explosion', 'fire_ball', 'no_factors')),
        },
        3: {  # СУГ токсич
            'partial': (
                (0.0350, 0.0083, 0.0264, 0.9303), ('liguid_jet', 'explosion', 'flash', 'toxi')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('liguid_jet', 'explosion', 'fire_ball', 'toxi')),
        },
        4: {  # ГЖ
            'partial': ((0.2, 0.04, 0.76), ('strait_fire', 'strait_fire', 'no_factors')),
            'full': ((0.2, 0.04, 0.76), ('strait_fire', 'strait_fire', 'no_factors')),
        },
        5: {  # ГГ
            'partial':
                ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'no_factors')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('gas_jet', 'explosion', 'flash', 'no_factors')),
        },
        6: {  # ГГ токсичный
            'partial':
                ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'toxi')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('gas_jet', 'explosion', 'flash', 'toxi')),
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
    'Compressor': {
        0: {  # ЛВЖ
            'partial': None,
            'full': None,
        },
        1: {  # ЛВЖ токсичная
            'partial': None,
            'full': None,
        },
        2: {  # СУГ
            'partial': None,
            'full': None,
        },
        3: {  # СУГ токсич
            'partial': None,
            'full': None,
        },
        4: {  # ГЖ
            'partial': None,
            'full': None,
        },
        5: {  # ГГ
            'partial':
                ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'no_factors')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('gas_jet', 'explosion', 'flash', 'no_factors')),
        },
        6: {  # ГГ токсичный
            'partial':
                ((0.0350, 0.0083, 0.0264, 0.9303), ('gas_jet', 'explosion', 'flash', 'toxi')),
            'full': ((0.2, 0.1152, 0.0768, 0.6080), ('gas_jet', 'explosion', 'flash', 'toxi')),
        },
        7: {  # ХОВ
            'partial': ((1.0,), ('toxi_spill',)),
            'full': ((1.0,), ('toxi_spill',))
        }
    },
}


def validate_equipment_substance_mapping(data):
    errors = []

    for equipment_type, substances in data.items():
        for substance_id, depressurization in substances.items():
            # Проверяем partial
            if depressurization['partial'] is not None:
                probabilities = depressurization['partial'][0]
                methods = depressurization['partial'][1]

                # Проверка суммы вероятностей
                prob_sum = sum(probabilities)
                if abs(prob_sum - 1.0) > 0.0001:  # используем погрешность для сравнения float
                    errors.append(
                        f"ERROR: {equipment_type}, substance {substance_id}, partial - сумма вероятностей = {prob_sum}")

                # Проверка равенства длин кортежей
                if len(probabilities) != len(methods):
                    errors.append(
                        f"ERROR: {equipment_type}, substance {substance_id}, partial - разная длина кортежей: "
                        f"вероятности {len(probabilities)}, методы {len(methods)}")

            # Проверяем full
            if depressurization['full'] is not None:
                probabilities = depressurization['full'][0]
                methods = depressurization['full'][1]

                # Проверка суммы вероятностей
                prob_sum = sum(probabilities)
                if abs(prob_sum - 1.0) > 0.0001:
                    errors.append(
                        f"ERROR: {equipment_type}, substance {substance_id}, full - сумма вероятностей = {prob_sum}")

                # Проверка равенства длин кортежей
                if len(probabilities) != len(methods):
                    errors.append(f"ERROR: {equipment_type}, substance {substance_id}, full - разная длина кортежей: "
                                  f"вероятности {len(probabilities)}, методы {len(methods)}")

    return errors






if __name__ == '__main__':
    # Запускаем проверку
    errors = validate_equipment_substance_mapping(equipment_substance_mapping)

    if errors:
        print("Найдены ошибки в данных:")
        for error in errors:
            print(error)
    else:
        print("Все данные корректны!")

    # Дополнительно выведем статистику по каждому оборудованию
    print("\nСтатистика по оборудованию:")
    for equipment_type in equipment_substance_mapping:
        substances = equipment_substance_mapping[equipment_type]
        valid_partial = sum(1 for s in substances.values() if s['partial'] is not None)
        valid_full = sum(1 for s in substances.values() if s['full'] is not None)
        print(f"{equipment_type}:")
        print(f"  Веществ с partial разгерметизацией: {valid_partial}")
        print(f"  Веществ с full разгерметизацией: {valid_full}")

