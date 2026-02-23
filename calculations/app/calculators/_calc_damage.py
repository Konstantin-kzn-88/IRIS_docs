from typing import Callable


def calculate_damage(
        scenario: dict,
        *,
        damage_coeffs: list[float],
        damage_func: Callable[[float, int, int], dict],
) -> dict:
    """
    Унифицированный блок ущерба:
    - выбираем k по scenario_line
    - считаем mass_for_damage = k * amount_t
    - вызываем damage()
    - раскладываем по полям result
    """
    # дефолты на всякий случай
    result = {}
    result.setdefault("direct_losses", None)
    result.setdefault("liquidation_costs", None)
    result.setdefault("social_losses", None)
    result.setdefault("indirect_damage", None)
    result.setdefault("total_environmental_damage", None)
    result.setdefault("total_damage", None)

    sc_line = int(scenario.get("scenario_line", 0))
    if 1 <= sc_line <= len(damage_coeffs):
        k = float(damage_coeffs[sc_line - 1])
    else:
        k = 0.0

    amount_t = float(result.get("amount_t", 0.0))

    base_damage = damage_func(
        amount_t,
        int(result.get("fatalities_count", 0) or 0),
        int(result.get("injured_count", 0) or 0),
        k=k,
    )

    result["direct_losses"] = base_damage["direct_losses"]
    result["liquidation_costs"] = base_damage["liquidation_costs"]
    result["social_losses"] = base_damage["social_losses"]
    result["indirect_damage"] = base_damage["indirect_damage"]
    result["total_environmental_damage"] = base_damage["total_environmental_damage"]
    result["total_damage"] = base_damage["total_damage"]

    return result
