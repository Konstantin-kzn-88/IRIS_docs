import math
from calculations.config import P0, R

def saturated_vapor_pressure_pa(Tk_C: float, Tp_C: float) -> float:
    """
    Давление насыщенных паров по Клаузиусу–Клапейрону (ГОСТ Р 12.3.047).
    """
    Tk = Tk_C + 273.15
    Tp = Tp_C + 273.15
    return P0 * math.exp((R / Tk) * (1.0 / Tp - 1.0 / Tk))


def evaporation_intensity_kg_m2_s(
    Pn_pa: float,
    M_kg_per_mol: float,
    eta: float = 1.0
) -> float:
    """
    Интенсивность испарения ненагретой жидкости, кг/(м²·с)
    """
    return 1e-6 * eta * Pn_pa * math.sqrt(M_kg_per_mol)