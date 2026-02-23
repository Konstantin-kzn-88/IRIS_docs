from core.config import PEOPLE_COUNT


def calculate_risk(result: dict) -> None:
    """
    Унифицированный блок рисков (как у тебя везде):
    collective_* = count * scenario_frequency
    individual_* = collective / PEOPLE_COUNT
    expected_value = total_damage * scenario_frequency
    """
    result["collective_risk_fatalities"] = (result["fatalities_count"] or 0) * result["scenario_frequency"]
    result["collective_risk_injured"] = (result["injured_count"] or 0) * result["scenario_frequency"]
    result["expected_value"] = (result["total_damage"] or 0) * result["scenario_frequency"]

    result["individual_risk_fatalities"] = result["collective_risk_fatalities"] / PEOPLE_COUNT
    result["individual_risk_injured"] = result["collective_risk_injured"] / PEOPLE_COUNT