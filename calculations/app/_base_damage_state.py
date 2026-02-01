import math


def __calculate_direct_losses_log(mass: float) -> float:
    if mass <= 0:
        return 0

    # Настраиваемые параметры
    scale = 18000  # общий масштаб ущерба
    log_base = 1.8  # чем больше — тем быстрее насыщение

    if mass < 1:
        return mass * 120  # очень маленькие разливы — почти линейно и дорого

    return scale * math.log(1 + mass) ** log_base


def damage(mass, count_dead_personal, count_injured_personal):
    result = {}

    result["direct_losses"] =__calculate_direct_losses_log(mass)

    result["liquidation_costs"] = result["direct_losses"] * 0.1
    result["social_losses"] = count_dead_personal * 3000 + count_injured_personal * 250
    result["indirect_damage"] = 0.157 * result["social_losses"]
    result["total_environmental_damage"] = result["direct_losses"] * 0.236
    result["total_damage"] = result["direct_losses"] + result["liquidation_costs"] + result["social_losses"] + result[
        "indirect_damage"] + result["total_environmental_damage"]
    return result
