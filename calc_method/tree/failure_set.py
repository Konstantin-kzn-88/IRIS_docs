# Модуль с данными по частотам отказов оборудования
# @version: 1.0
# @date: 2024-01-06
# ------------------------------------------------------------------------------------
# @author: Generated from SQL data
# ------------------------------------------------------------------------------------

# type_id в данных:
# 1: Частичная разгерметизация
# 2: Полная разгерметизация

equipment_failure_rates = {
    'Pipeline': {
        'categories': {
            'Менее 75 мм': {
                'partial': 2.4E-6,
                'full': 5.7E-7
            },
            'От 75 до 150 мм': {
                'partial': 1.1E-6,
                'full': 2.7E-7
            },
            'Более 150 мм': {
                'partial': 3.7E-7,
                'full': 8.8E-8
            }
        }
    },
    'Pump': {
        'categories': {
            'Центробежные герметичные': {
                'partial': 5.0E-4,
                'full': 1.0E-4
            },
            'Центробежные с уплотнениями': {
                'partial': 2.5E-3,
                'full': 5.0E-4
            },
            'Поршневые': {
                'partial': 2.5E-3,
                'full': 5.0E-4
            }
        }
    },
    'Technological_device': {
        'categories': {
            'Сосуды хранения под давлением': {
                'partial': 1.0E-4,
                'full': 5.7E-7
            },
            'Технологические аппараты': {
                'partial': 5.0E-4,
                'full': 1.0E-4
            },
            'Химические реакторы': {
                'partial': 5.0E-4,
                'full': 1.0E-4
            }
        }
    },
    'Tank': {
        'categories': {
            'Одностенный': {
                'partial': 5.0E-4,
                'full': 1.0E-4
            },
            'С внешней защитной оболочкой': {
                'partial': 5.0E-4,
                'full': 5.7E-7
            },
            'С двойной оболочкой': {
                'partial': 5.0E-4,
                'full': 2.5E-5
            },
            'Полной герметизации': {
                'partial': 5.0E-4,
                'full': 1.0E-5
            }
        }
    },
    'Truck_tank': {
        'categories': {
            'Под избыточным давлением': {
                'partial': 5.0E-7,
                'full': 5.0E-7
            },
            'При атмосферном давлении': {
                'partial': 5.0E-7,
                'full': 1.0E-4
            }
        }
    }
}


def validate_failure_rates(data):
    """
    Проверяет корректность данных в структуре частот отказов

    Args:
        data (dict): Словарь с данными по частотам отказов

    Returns:
        list: Список найденных ошибок
    """
    errors = []

    for equipment_type, equipment_data in data.items():
        if 'categories' not in equipment_data:
            errors.append(f"ERROR: {equipment_type} не содержит ключ 'categories'")
            continue

        for category, rates in equipment_data['categories'].items():
            if 'partial' not in rates:
                errors.append(f"ERROR: {equipment_type}, {category} не содержит частоту частичной разгерметизации")
            if 'full' not in rates:
                errors.append(f"ERROR: {equipment_type}, {category} не содержит частоту полной разгерметизации")

            # Проверка на отрицательные значения
            if rates.get('partial', 0) < 0:
                errors.append(
                    f"ERROR: {equipment_type}, {category} содержит отрицательную частоту частичной разгерметизации")
            if rates.get('full', 0) < 0:
                errors.append(
                    f"ERROR: {equipment_type}, {category} содержит отрицательную частоту полной разгерметизации")

    return errors


if __name__ == '__main__':
    # Запускаем проверку
    errors = validate_failure_rates(equipment_failure_rates)

    if errors:
        print("Найдены ошибки в данных:")
        for error in errors:
            print(error)
    else:
        print("Все данные корректны!")

    # Выводим статистику
    print("\nСтатистика по оборудованию:")
    for equipment_type, equipment_data in equipment_failure_rates.items():
        categories_count = len(equipment_data['categories'])
        print(f"{equipment_type}:")
        print(f"  Количество категорий: {categories_count}")