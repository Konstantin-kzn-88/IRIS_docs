from ._base_cost_for_damage import approx_equipment_cost
from core.config import DAMAGE_SCALE

def damage(mass, count_dead_personal, count_injured_personal, k: float = 1.0):
    result= {}
    # базовые расчёты
    direct = approx_equipment_cost(mass) * DAMAGE_SCALE
    liquidation = direct * 0.1
    environmental = direct * 0.236

    social = count_dead_personal * 3000 + count_injured_personal * 250
    indirect = 0.157 * social

    # масштабируем только зависящие от масштаба аварии
    direct *= k
    liquidation *= k
    environmental *= k

    result["direct_losses"] = direct
    result["liquidation_costs"] = liquidation
    result["social_losses"] = social
    result["indirect_damage"] = indirect
    result["total_environmental_damage"] = environmental

    result["total_damage"] = (
        direct
        + liquidation
        + social
        + indirect
        + environmental
    )

    return result