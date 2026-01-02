def damage(mass, count_dead_personal, count_injured_personal):
    result = {}
    result["direct_losses"] = mass * 112.23
    result["liquidation_costs"] = result["direct_losses"] * 0.1
    result["social_losses"] = count_dead_personal * 3000 + count_injured_personal * 250
    result["indirect_damage"] = 0.157 * result["social_losses"]
    result["total_environmental_damage"] = mass * 50.236
    result["total_damage"] = result["direct_losses"] + result["liquidation_costs"] + result["social_losses"] + result[
        "indirect_damage"] + result["total_environmental_damage"]
    return result
