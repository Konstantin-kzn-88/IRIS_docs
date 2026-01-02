def count_dead_personal(radius):
    if radius < 20:
        return 1
    elif radius >= 20 and radius <= 30:
        return 2
    elif radius > 30:
        return 3
