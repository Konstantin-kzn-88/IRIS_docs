def cost_large_tank(V):
    return 85_000 * (V ** 0.62)

def cost_small_tank(V):
    return 22_000 * (V ** 0.78) + 45_000

def approx_equipment_cost(V: float) -> float:
    if V <= 0:
        return 0.0
    if V <= 100:
        return cost_small_tank(V)
    else:
        return cost_large_tank(V)/1000