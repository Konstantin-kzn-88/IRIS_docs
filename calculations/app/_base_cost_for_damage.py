def approx_equipment_cost(V: float) -> float:
    if V <= 0:
        return 0.0

    V0, y0 = 0.1, 100.0
    Vb = 1000.0
    m1 = 1.0

    if V <= Vb:
        return y0 + m1 * (V - V0)

    yb = y0 + m1 * (Vb - V0)
    m2 = (25000.0 - yb) / (10000.0 - Vb)
    return yb + m2 * (V - Vb)