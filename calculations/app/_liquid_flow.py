import math
from calculations.config import CD

def liquid_leak_mass_flow(p_mpa, d_mm, rho):
    p = p_mpa * 1e6          # МПа → Па
    d = d_mm / 1000          # мм → м
    A = math.pi * d**2 / 4
    m_dot = CD * A * math.sqrt(2 * rho * p)
    return m_dot  # кг/с