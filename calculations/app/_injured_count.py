def count_injured_personal(radius):
    if radius < 20:
        return 2
    elif radius >= 20 and radius <= 30:
        return 3
    elif radius > 30:
        return 4