def get_nearest_value(iterable, value):
    return min(iterable, key=lambda x: abs(x - value))