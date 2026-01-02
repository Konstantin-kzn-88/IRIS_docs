import math
from calculations.config import P0, R


def saturated_vapor_pressure_pa(
    Tk_C: float,
    Tp_C: float,
    evaporation_heat_J_per_kg: float,
    molar_mass_kg_per_mol: float,
    P_ref_pa: float = P0
) -> float:
    """
    Давление насыщенных паров по уравнению Клаузиуса–Клапейрона
    (с сохранением "старой" позиционной сигнатуры).

    Аргументы и единицы:
      - Tk_C: текущая температура, °C
      - Tp_C: опорная температура, °C (обычно boiling_point_C)
      - evaporation_heat_J_per_kg: удельная теплота испарения, Дж/кг
      - molar_mass_kg_per_mol: молярная масса, кг/моль
      - P_ref_pa: давление насыщенных паров при Tp_C, Па (по умолчанию P0)

    Физика и связь с БД:
      - В БД задана теплота испарения в Дж/кг и молярная масса в кг/моль.
        Для К-К нужна молярная теплота: ΔH_molar = L * M (Дж/моль).

    Формула:
      ln(P/P_ref) = -ΔH_molar/R * (1/Tk - 1/Tp)
    """
    Tk = Tk_C + 273.15
    Tp = Tp_C + 273.15

    # Защита от некорректных значений (не меняет логику при валидных входных данных)
    if Tk <= 0 or Tp <= 0:
        raise ValueError("Temperature in Kelvin must be positive.")
    if evaporation_heat_J_per_kg <= 0 or molar_mass_kg_per_mol <= 0:
        raise ValueError("Evaporation heat and molar mass must be positive.")
    if P_ref_pa <= 0:
        raise ValueError("Reference pressure must be positive.")

    delta_h_molar = evaporation_heat_J_per_kg * molar_mass_kg_per_mol  # Дж/моль
    return P_ref_pa * math.exp(-(delta_h_molar / R) * (1.0 / Tk - 1.0 / Tp))


def evaporation_intensity_kg_m2_s(
    Pn_pa: float,
    molar_mass_kg_per_mol: float,
    eta: float = 1.0
) -> float:
    """
    Интенсивность испарения ненагретой жидкости, кг/(м²·с).

    Используется методическая форма: m_dot = 1e-6 * eta * Pn * sqrt(M),
    где M подставляется численно в г/моль (эквивалентно кг/кмоль).

    В БД молярная масса хранится в кг/моль, поэтому:
      M_g_per_mol = molar_mass_kg_per_mol * 1000.
    """
    if Pn_pa < 0:
        raise ValueError("Saturated vapor pressure must be non-negative.")
    if molar_mass_kg_per_mol <= 0:
        raise ValueError("Molar mass must be positive.")
    if eta <= 0:
        raise ValueError("Evaporation coefficient eta must be positive.")

    molar_mass_g_per_mol = molar_mass_kg_per_mol * 1_000.0
    Pn_kpa = Pn_pa / 1_000.0
    return 1e-6 * eta * Pn_kpa * math.sqrt(molar_mass_g_per_mol)
