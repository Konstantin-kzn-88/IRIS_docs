# utilities/equipment_name_validator.py

"""
Модуль для валидации названий оборудования.
Обеспечивает проверку формата "Название (Компонент)" и извлечение компонента.
"""

import re


def validate_equipment_name(name: str) -> tuple[bool, str]:
    """
    Проверяет формат названия оборудования

    Args:
        name: название оборудования в формате "Название (Компонент)"

    Returns:
        tuple[bool, str]: (валидно ли название, сообщение об ошибке)
    """
    # Проверяем базовое название
    if not name.strip():
        return False, "Наименование не может быть пустым"

    # Проверяем формат "Название (Компонент)"
    pattern = r'^.+\([^()]+\)$'
    if not re.match(pattern, name):
        return False, "Формат должен быть: 'Название (Составляющая)'"

    # Проверяем что в скобках что-то есть
    match = re.search(r'\((.*?)\)', name)
    if not match or not match.group(1).strip():
        return False, "Составляющая в скобках не может быть пустая"

    return True, ""


def extract_component(name: str) -> str:
    """
    Извлекает название компонента из полного названия оборудования

    Args:
        name: полное название оборудования в формате "Название (Компонент)"

    Returns:
        str: название компонента или пустая строка, если формат неверный
    """
    match = re.search(r'\((.*?)\)', name)
    return match.group(1).strip() if match else ""