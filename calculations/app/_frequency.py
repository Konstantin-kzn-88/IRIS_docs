from __future__ import annotations

from core.config import (
    WITHOUT_ACTIVITES_COMPENSATOIRES,
    WITH_ACTIVITES_COMPENSATOIRES,
)


def apply_ac_multiplier(scenario: dict, hazard_component: str) -> dict:
    """
    Возвращает КОПИЮ scenario, где scenario_frequency домножена на AC-множитель
    в зависимости от hazard_component.
    """
    sc = dict(scenario)  # копия, чтобы не портить исходный список сценариев

    base_freq = sc.get("base_frequency", 1)
    accident_event_probability = sc.get("accident_event_probability", 1)
    hc = hazard_component or ""

    if "(без КМ)" in hc:
        sc["base_frequency"] = base_freq * WITHOUT_ACTIVITES_COMPENSATOIRES
        sc["scenario_frequency"] = base_freq * accident_event_probability * WITHOUT_ACTIVITES_COMPENSATOIRES
    elif "(с КМ)" in hc:
        sc["base_frequency"] = base_freq * WITH_ACTIVITES_COMPENSATOIRES
        sc["scenario_frequency"] = base_freq * accident_event_probability * WITH_ACTIVITES_COMPENSATOIRES
    else:
        sc["base_frequency"] = base_freq
        sc["scenario_frequency"] = base_freq * accident_event_probability

    return sc
