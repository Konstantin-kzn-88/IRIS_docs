def get_nearest_value(iterable, value):
    """
    Находит ближайшее значение к заданному в итерируемом объекте

    Args:
        iterable: Итерируемый объект с числами
        value: Значение, к которому ищем ближайшее

    Returns:
        Ближайшее значение из iterable к value

    Raises:
        ValueError: Если iterable пустой
    """
    if not iterable:
        raise ValueError("Итерируемый объект не может быть пустым")

    return min(iterable, key=lambda x: abs(x - value))