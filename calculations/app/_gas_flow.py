import math
from calculations.config import CD, R, K_ADIABAT


def gas_leak_mass_flow(
        p_mpa,  # давление в аппарате, МПа (абс)
        d_mm,  # диаметр отверстия, мм
        T_c,  # температура газа, °C
        molar_mass,  # молярная масса, кг/моль
):
    """
    Массовый расход газа при критическом истечении
    """
    p = p_mpa * 1e6  # Па
    d = d_mm / 1000  # м
    A = math.pi * d ** 2 / 4
    T = T_c + 273.15  # К

    R_calc = R / molar_mass  # Дж/(кг·К)

    m_dot = (
            CD * A * p *
            math.sqrt(
                K_ADIABAT / (R_calc * T) *
                (2 / (K_ADIABAT + 1)) ** ((K_ADIABAT + 1) / (K_ADIABAT - 1))
            )
    )

    return m_dot  # кг/с
