"""
Расчёт энергетического показателя технологического блока.
(методика: пункты 1.1 и 1.2 из предоставленного фрагмента)

--------------------------------------------------------------------------
П. 1.1. Энергия ПГФ, находящейся в блоке:

    E1' = G1' * q + A

где:
    G1' — масса ПГФ, приведённая к условиям после адиабатического расширения, кг
    q   — удельная теплота сгорания ПГФ, кДж/кг
    A   — энергия адиабатического расширения, кДж

Энергия расширения:
    A = (1/(k-1)) * P*V' * [ 1 - (P0/P)^((k-1)/k) ]
или A = β1 * P*V', где
    β1 = (1/(k-1)) * [ 1 - (P0/P)^((k-1)/k) ]

Масса ПГФ:
    G1' = V0' * ρ0'
    V0' = (P/P0) * (V'/T') * T
    T   = T1 * (P0/P)^((k-1)/k)
    ρ0' = ρ * (P0/P)^(1/k)

--------------------------------------------------------------------------
П. 1.2. Энергия сгорания ПГФ, поступившей к разгерметизированному участку
от смежных объектов (блоков):

    E2' = Σ (Gi' * qi')

Для i-го потока:
    Gi' = ρi' * wi' * Si' * τi

Скорость истечения wi' (в методике даны две формулы):
    1) при избыточном давлении Pизб <= 0.07 МПа:
        wi' = sqrt( (2k/(k+1)) * (Pi'/ρi') )
    2) в общем случае:
        wi' = sqrt( (2k/(k-1)) * (Pi'/ρi') * [1 - (P0/Pi')^((k-1)/k)] )


--------------------------------------------------------------------------
П. 1.3. Энергия сгорания ПГФ, образующейся за счёт энергии перегретой ЖФ
рассматриваемого блока и поступившей от смежных объектов за время τi, кДж:

    E3' = G1'' * [1 - exp(-c1 * θk / r1)] * q1
          + Σ (Gi'' * [1 - exp(-c1 * θk_i / r_i)] * qi)

где:
    G1''  — количество (масса) перегретой жидкой фазы (ЖФ) в рассматриваемом блоке, кг
    Gi''  — количество (масса) ЖФ, поступившей от смежного i-го блока за время τi, кг
    c1    — эмпирический коэффициент (задаётся по методике/данным), 1/с (или согласованные единицы)
    θk    — «контактное/характерное» время (или параметр процесса), с (или согласованные единицы)
    r     — характерный размер/параметр, м (или согласованные единицы)
    q     — удельная теплота сгорания, кДж/кг

Количество ЖФ от смежных блоков:
    Gi'' = ρi'' * wi'' * Si'' * τi

Скорость истечения ЖФ:
    wi'' = μ * sqrt( 2 * ΔP / ρi'' )

где:
    μ   — коэффициент, учитывающий реальные свойства ЖФ и гидравлические условия (обычно 0.4...0.8)
    ΔP  — избыточное давление истечения ЖФ, Па (в исходных данных можно задавать в МПа и переводить)

В коде для универсальности все параметры c1, θ, r задаются как входные величины.
--------------------------------------------------------------------------

--------------------------------------------------------------------------
ОГРАНИЧЕНИЕ РАСЧЁТА (принято в данной реализации)

В рамках данной программы НЕ рассчитываются:

1) Энергия сгорания ПГФ, образующейся из ЖФ за счёт тепла
   экзотермических химических реакций, не прекращающихся
   при разгерметизации оборудования.

2) Энергия сгорания ПГФ, образующейся из ЖФ за счёт
   теплопритока от внешних теплоносителей.

Указанные составляющие энергетического показателя
в данной модели сознательно исключены, поскольку
по постановке задачи они не требуются.
--------------------------------------------------------------------------

--------------------------------------------------------------------------
П. 1.6. Энергия сгорания ПГФ, образующейся из пролитой на твёрдую поверхность
ЖФ за счёт тепло- и массообмена с окружающей средой, кДж.

    E4' = GΣ'' * q'

где суммарная масса парогазовой фазы:

    GΣ'' = G4'' + G5''

1) За счёт теплопередачи от подстилающей поверхности:

    G4'' = 2 * (T0 - Tk) / r * (ε / sqrt(π)) * Fп * sqrt(τи)

    ε = sqrt(λ ρ c)

2) За счёт испарения в атмосферу:

    G5'' = mн * Fж * τи

    mн = 10^-6 * η * Pн / sqrt(M)

    Pн = P0 * exp( r/R * (1/Tk - 1/Tp) )

В данной реализации формулы приведены в вычислимый вид.
--------------------------------------------------------------------------
--------------------------------------------------------------------------
ВАЖНО ПРО ЕДИНИЦЫ:
- В исходных данных давление P и P0 задаём в МПа (абсолютное давление).
- Объём V' — м³, температура — К, плотность — кг/м³, площадь — м², время — с.
- Для энергии расширения A:
      1 МПа·м³ = 10^6 Па·м³ = 10^6 Дж = 1000 кДж
  поэтому при вычислении A в (МПа·м³) умножаем на 1000, чтобы получить кДж.

--------------------------------------------------------------------------
ОСОБЫЕ УСЛОВИЯ (из методики):
Для п. 1.1 допускается не учитывать A при малости значений:
- Pизб < 0.07 МПа  И  P*V' < 0.02 МПа·м³

В коде это реализовано.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import math


# ======================================================================
# БЛОК ИСХОДНЫХ ДАННЫХ (п. 1.1)
# ======================================================================

@dataclass(frozen=True)
class BlockData:
    """
    Исходные данные для расчёта п. 1.1 (ПГФ, находящаяся в блоке).

    Поля подобраны так, чтобы напрямую подставляться в формулы методики.

    P_mpa
        Абсолютное давление в блоке, МПа.
    P0_mpa
        Атмосферное (или опорное) абсолютное давление, МПа.
        Обычно P0 ≈ 0.1 МПа.
    V_m3
        Объём ПГФ в блоке V', м³.
    T1_K
        Температура ПГФ в блоке до расширения T1, К.
        В формуле V0' используется T' — по смыслу это температура в блоке,
        т.е. T' = T1 (если методика не задаёт иной).
    rho_kg_m3
        Плотность ПГФ при P и T1 (в блоке), кг/м³.
    k
        Показатель адиабаты (безразмерный), например 1.25...1.35 для
        многих углеводородных газов (точное значение задайте по данным).
    q_kj_kg
        Удельная теплота сгорания ПГФ, кДж/кг.
    """

    P_mpa: float
    P0_mpa: float
    V_m3: float
    T1_K: float
    rho_kg_m3: float
    k: float
    q_kj_kg: float

    # Дополнительные поля для "полной цепочки" по методике (опционально):
    air_speed_m_s: float = 0.0  # скорость воздуха над зеркалом испарения, м/с
    air_temp_c: float = 20.0  # температура воздуха, °C (для η)
    Tp_K: float | None = None  # расчётная температура Tp (К). Если None, берём max(T0, Tk) как приближение.
    P0_kpa: float = 101.3  # базовое давление P0 в формуле насыщ. пара, кПа
    R_j_mol_K: float = 8.314  # универсальная газовая постоянная, Дж/(моль·К)
    r_j_mol: float | None = None  # теплота испарения в Дж/моль для формулы Pн; если None, Pн берётся из Pn_kpa
    use_calc_Pn: bool = False  # если True и r_j_mol задан, считаем Pн по формуле (вместо ввода)
    use_table_eta: bool = False  # если True, берём η из таблицы №1 по air_speed_m_s и air_temp_c


# ======================================================================
# БЛОК ИСХОДНЫХ ДАННЫХ (п. 1.2)
# ======================================================================

@dataclass(frozen=True)
class FlowData:
    """
    Исходные данные одного поступающего потока (i-й поток) для п. 1.2.

    Pi_mpa
        Абсолютное давление потока, МПа.
    rho_kg_m3
        Плотность потока ρi', кг/м³ (в условиях потока для формулы Gi').
    S_m2
        Площадь сечения (отверстия/канала) Si', м².
    tau_s
        Время поступления/истечения τi, с.
    k
        Показатель адиабаты k (безразмерный).
    q_kj_kg
        Удельная теплота сгорания qi', кДж/кг.
    """

    Pi_mpa: float
    rho_kg_m3: float
    S_m2: float
    tau_s: float
    k: float
    q_kj_kg: float


# ======================================================================
# ВСПОМОГАТЕЛЬНЫЕ ПРОВЕРКИ
# ======================================================================

def _require_positive(name: str, value: float) -> None:
    """Базовая проверка на положительность параметра."""
    if value <= 0:
        raise ValueError(f"{name} должно быть > 0, получено: {value}")


def _require_non_negative(name: str, value: float) -> None:
    """Базовая проверка на неотрицательность параметра."""
    if value < 0:
        raise ValueError(f"{name} должно быть >= 0, получено: {value}")


# ======================================================================
# П. 1.1 — РАСЧЁТНЫЕ ФУНКЦИИ
# ======================================================================

def beta1(P_mpa: float, P0_mpa: float, k: float) -> float:
    """
    β1 = (1/(k-1)) * (1 - (P0/P)^((k-1)/k))

    Все величины безразмерны/в МПа, т.к. входит только отношение P0/P.
    """
    _require_positive("P_mpa", P_mpa)
    _require_positive("P0_mpa", P0_mpa)
    _require_positive("k", k)
    if math.isclose(k, 1.0):
        raise ValueError("k не должен быть равен 1 (деление на (k-1))")
    if P0_mpa > P_mpa:
        # Теоретически возможно для разрежения, но в большинстве задач по методике
        # рассчитывают истечение/расширение из области более высокого давления.
        raise ValueError("Ожидается P_mpa >= P0_mpa (абсолютные давления)")

    return (1.0 / (k - 1.0)) * (1.0 - (P0_mpa / P_mpa) ** ((k - 1.0) / k))


def adiabatic_expansion_energy_kj(data: BlockData) -> float:
    """
    Энергия адиабатического расширения A, кДж.

    A = β1 * P * V'   (в МПа·м³), далее *1000 => кДж
    Также реализовано условие, когда A допускается не учитывать.
    """
    # Проверки входных данных (минимально необходимые):
    _require_positive("P_mpa", data.P_mpa)
    _require_positive("P0_mpa", data.P0_mpa)
    _require_positive("V_m3", data.V_m3)
    _require_positive("k", data.k)

    P_excess_mpa = data.P_mpa - data.P0_mpa  # избыточное давление, МПа
    PV_mpa_m3 = data.P_mpa * data.V_m3  # P*V', МПа·м³

    # Условие методики: A можно не учитывать при малости Pизб и PV.
    if P_excess_mpa < 0.07 and PV_mpa_m3 < 0.02:
        return 0.0

    b1 = beta1(data.P_mpa, data.P0_mpa, data.k)

    # 1 МПа·м³ = 1000 кДж
    A_kj = b1 * PV_mpa_m3 * 1000.0
    return A_kj


def mass_after_expansion_kg(data: BlockData) -> float:
    """
    Масса ПГФ G1', кг, по формулам методики:

        T   = T1 * (P0/P)^((k-1)/k)
        ρ0' = ρ  * (P0/P)^(1/k)
        V0' = (P/P0) * (V'/T1) * T
        G1' = V0' * ρ0'

    В коде:
    - T1_K используется как T' в формуле V0' (как на фрагменте методики).
    """
    _require_positive("P_mpa", data.P_mpa)
    _require_positive("P0_mpa", data.P0_mpa)
    _require_positive("V_m3", data.V_m3)
    _require_positive("T1_K", data.T1_K)
    _require_positive("rho_kg_m3", data.rho_kg_m3)
    _require_positive("k", data.k)

    # Температура после адиабатического расширения
    T_K = data.T1_K * (data.P0_mpa / data.P_mpa) ** ((data.k - 1.0) / data.k)

    # Плотность после расширения
    rho0_kg_m3 = data.rho_kg_m3 * (data.P0_mpa / data.P_mpa) ** (1.0 / data.k)

    # Приведение объёма к «нормальным/опорным» условиям, как в методике
    V0_m3 = (data.P_mpa / data.P0_mpa) * (data.V_m3 / data.T1_K) * T_K

    # Масса
    G1_kg = V0_m3 * rho0_kg_m3
    return G1_kg


def energy_in_block_kj(data: BlockData) -> Tuple[float, float, float]:
    """
    Итог для п. 1.1:
        E1' = G1' * q + A

    Возвращаем кортеж:
        (E1_kj, G1_kg, A_kj)
    """
    _require_positive("q_kj_kg", data.q_kj_kg)

    G1 = mass_after_expansion_kg(data)
    A = adiabatic_expansion_energy_kj(data)
    E1 = G1 * data.q_kj_kg + A
    return E1, G1, A


# ======================================================================
# П. 1.2 — РАСЧЁТНЫЕ ФУНКЦИИ
# ======================================================================

def outflow_velocity_m_s(flow: FlowData, P0_mpa: float) -> float:
    """
    Скорость истечения wi' по методике (две формулы).

    В формулах используется отношение P0/P, поэтому достаточно абсолютных давлений.
    Но величина Pi'/ρi' должна быть в согласованных единицах.
    Чтобы получить скорость в м/с, Pi' переводим в Па:
        1 МПа = 1_000_000 Па
    """
    _require_positive("Pi_mpa", flow.Pi_mpa)
    _require_positive("P0_mpa", P0_mpa)
    _require_positive("rho_kg_m3", flow.rho_kg_m3)
    _require_positive("k", flow.k)
    if math.isclose(flow.k, 1.0):
        raise ValueError("k не должен быть равен 1 (деление на (k-1))")
    if flow.Pi_mpa < P0_mpa:
        raise ValueError("Ожидается Pi_mpa >= P0_mpa (абсолютные давления)")

    P_excess_mpa = flow.Pi_mpa - P0_mpa

    Pi_pa = flow.Pi_mpa * 1_000_000.0
    P0_pa = P0_mpa * 1_000_000.0

    if P_excess_mpa <= 0.07:
        # Упрощённая формула при малом избыточном давлении
        w = math.sqrt((2.0 * flow.k / (flow.k + 1.0)) * (Pi_pa / flow.rho_kg_m3))
    else:
        # Общая формула
        w = math.sqrt(
            (2.0 * flow.k / (flow.k - 1.0))
            * (Pi_pa / flow.rho_kg_m3)
            * (1.0 - (P0_pa / Pi_pa) ** ((flow.k - 1.0) / flow.k))
        )
    return w


def flow_mass_kg(flow: FlowData, P0_mpa: float) -> float:
    """
    Масса i-го потока:
        Gi' = ρi' * wi' * Si' * τi
    """
    _require_positive("S_m2", flow.S_m2)
    _require_non_negative("tau_s", flow.tau_s)

    w = outflow_velocity_m_s(flow, P0_mpa)
    G = flow.rho_kg_m3 * w * flow.S_m2 * flow.tau_s
    return G


def energy_from_adjacent_blocks_kj(flows: List[FlowData], P0_mpa: float) -> Tuple[float, List[float]]:
    """
    Энергия по п. 1.2:
        E2' = Σ(Gi' * qi')

    Возвращаем:
        (E2_kj, masses_kg)
    где masses_kg — список масс потоков Gi' (по порядку входного списка).
    """
    _require_positive("P0_mpa", P0_mpa)

    total = 0.0
    masses: List[float] = []

    for idx, flow in enumerate(flows, start=1):
        _require_positive(f"flows[{idx}].q_kj_kg", flow.q_kj_kg)
        Gi = flow_mass_kg(flow, P0_mpa)
        masses.append(Gi)
        total += Gi * flow.q_kj_kg

    return total, masses


# ======================================================================
# П. 1.3 — РАСЧЁТНЫЕ ФУНКЦИИ (перегретая жидкая фаза, ЖФ)
# ======================================================================

@dataclass(frozen=True)
class OverheatedLiquidInBlock:
    """
    Данные по перегретой ЖФ, находящейся в рассматриваемом блоке (первое слагаемое в п.1.3).

    G_kg
        Масса перегретой ЖФ в блоке, кг (G1'').
    q_kj_kg
        Удельная теплота сгорания соответствующей ПГФ/паров/смеси, кДж/кг (q1).
    c1
        Коэффициент c1 (по методике/данным), 1/с (или согласованные единицы).
    theta_s
        Параметр θk (часто интерпретируют как время/характерное время), с.
    r_m
        Характерный параметр r1, м.
        (Важно: θ и r должны быть в согласованных единицах с c1.)
    """
    G_kg: float
    q_kj_kg: float
    c1: float
    theta_s: float
    r_m: float


@dataclass(frozen=True)
class LiquidFlowData:
    """
    Данные по поступающей перегретой ЖФ от смежного объекта (i-е слагаемое в п.1.3).

    rho_kg_m3
        Плотность ЖФ ρi'', кг/м³.
    S_m2
        Площадь сечения истечения Si'', м².
    tau_s
        Время поступления/истечения τi, с.
    deltaP_mpa
        Избыточное давление истечения ΔP, МПа (в расчёте переводим в Па).
    mu
        Коэффициент μ (0.4...0.8 по методике), безразмерный.
    q_kj_kg
        Удельная теплота сгорания qi, кДж/кг.
    c1, theta_s, r_m
        Параметры экспоненциального множителя [1 - exp(-c1*θ/r)] для данного потока.
    """
    rho_kg_m3: float
    S_m2: float
    tau_s: float
    deltaP_mpa: float
    mu: float
    q_kj_kg: float
    c1: float
    theta_s: float
    r_m: float


def _fraction_evaporated(c1: float, theta_s: float, r_m: float) -> float:
    """
    Вычисляет множитель:
        f = 1 - exp(-c1 * theta / r)

    Интерпретация:
    - f (0..1) — доля/вклад образования ПГФ за счёт энергии перегретой ЖФ.
    """
    _require_positive("c1", c1)
    _require_non_negative("theta_s", theta_s)
    _require_positive("r_m", r_m)

    # exp(0)=1 => при theta=0 получаем f=0, что физически разумно.
    return 1.0 - math.exp(-c1 * theta_s / r_m)


def liquid_outflow_velocity_m_s(deltaP_mpa: float, rho_kg_m3: float, mu: float) -> float:
    """
    Скорость истечения ЖФ по формуле:
        w'' = μ * sqrt( 2 * ΔP / ρ )

    Здесь:
    - ΔP задаём в МПа, внутри переводим в Па.
    - ρ — кг/м³
    - результат — м/с
    """
    _require_non_negative("deltaP_mpa", deltaP_mpa)
    _require_positive("rho_kg_m3", rho_kg_m3)
    _require_positive("mu", mu)

    deltaP_pa = deltaP_mpa * 1_000_000.0
    return mu * math.sqrt(2.0 * deltaP_pa / rho_kg_m3)


def liquid_flow_mass_kg(flow: LiquidFlowData) -> float:
    """
    Масса поступившей ЖФ (формула (8)):
        Gi'' = ρi'' * wi'' * Si'' * τi
    """
    _require_positive("rho_kg_m3", flow.rho_kg_m3)
    _require_positive("S_m2", flow.S_m2)
    _require_non_negative("tau_s", flow.tau_s)

    w = liquid_outflow_velocity_m_s(flow.deltaP_mpa, flow.rho_kg_m3, flow.mu)
    return flow.rho_kg_m3 * w * flow.S_m2 * flow.tau_s


def energy_from_overheated_liquid_kj(
        in_block: OverheatedLiquidInBlock | None,
        incoming_flows: List[LiquidFlowData] | None
) -> Tuple[float, float, List[float]]:
    """
    Энергия по п. 1.3 (условное имя E3').

    Возвращаем:
        (E3_kj, G1_kg, Gi_list_kg)

    где:
    - E3_kj      — энергия, кДж
    - G1_kg      — масса перегретой ЖФ в блоке (0 если in_block=None)
    - Gi_list_kg — список масс ЖФ по входящим потокам (пустой список если incoming_flows=None)
    """
    total = 0.0
    G1 = 0.0
    Gi_list: List[float] = []

    # 1) Перегретая ЖФ внутри блока
    if in_block is not None:
        _require_non_negative("G_kg (in_block)", in_block.G_kg)
        _require_positive("q_kj_kg (in_block)", in_block.q_kj_kg)

        f1 = _fraction_evaporated(in_block.c1, in_block.theta_s, in_block.r_m)
        G1 = in_block.G_kg
        total += G1 * f1 * in_block.q_kj_kg

    # 2) Поступившие потоки ЖФ
    if incoming_flows:
        for idx, flow in enumerate(incoming_flows, start=1):
            _require_positive(f"incoming_flows[{idx}].q_kj_kg", flow.q_kj_kg)
            _require_positive(f"incoming_flows[{idx}].mu", flow.mu)

            Gi = liquid_flow_mass_kg(flow)
            Gi_list.append(Gi)

            fi = _fraction_evaporated(flow.c1, flow.theta_s, flow.r_m)
            total += Gi * fi * flow.q_kj_kg

    return total, G1, Gi_list


# ======================================================================
# П. 1.6 — ПРОЛИВ НА ТВЁРДУЮ ПОВЕРХНОСТЬ
# ======================================================================

@dataclass(frozen=True)
class SpillEvaporationData:
    """
    Исходные данные для расчёта п.1.6

    T0_K      — температура подстилающей поверхности, К
    Tk_K      — температура кипения жидкости, К
    r         — теплота фазового перехода (или параметр из методики)
    lambda_W  — теплопроводность поверхности
    rho_kg_m3 — плотность материала поверхности
    c         — теплоёмкость поверхности
    Fp_m2     — площадь пролива, м²
    tau_s     — время испарения, с

    eta       — коэффициент по таблице №1
    Pn_kpa    — давление насыщенного пара, кПа
    M         — молярная масса
    q_kj_kg   — теплота сгорания, кДж/кг
    """

    T0_K: float
    Tk_K: float
    r: float
    lambda_W: float
    rho_kg_m3: float
    c: float
    Fp_m2: float
    tau_s: float
    eta: float
    Pn_kpa: float
    M: float
    q_kj_kg: float

    # дополнительные (опциональные)
    air_speed_m_s: float = 0.0
    air_temp_c: float = 20.0
    Tp_K: float | None = None
    P0_kpa: float = 101.3
    R_j_mol_K: float = 8.314
    r_j_mol: float | None = None
    use_calc_Pn: bool = False
    use_table_eta: bool = False


def saturated_vapor_pressure_kpa(P0_kpa: float, r_j_mol: float, R_j_mol_K: float, Tk_K: float, Tp_K: float) -> float:
    """
    Расчёт давления насыщенного пара Pн по формуле методики:

        Pн = P0 * exp( (r/R) * (1/Tk - 1/Tp) )

    Где:
    - P0_kpa  : базовое давление, кПа (в методике обозначено как P0)
    - r_j_mol : параметр r в Дж/моль (теплота испарения в молярном виде), либо согласованная величина
    - R_j_mol_K : универсальная газовая постоянная, Дж/(моль·К) (обычно 8.314)
    - Tk_K    : температура кипения, К
    - Tp_K    : расчётная температура, К (макс(Tвоздуха, Tжидкости))

    ВАЖНО:
    Эта формула чувствительна к размерностям r и R.
    Если в исходной методике r задаётся в других единицах (например, Дж/кг),
    нужно привести его к согласованной форме (обычно Дж/моль).
    """
    _require_positive("P0_kpa", P0_kpa)
    _require_positive("R_j_mol_K", R_j_mol_K)
    _require_positive("Tk_K", Tk_K)
    _require_positive("Tp_K", Tp_K)

    exponent = (r_j_mol / R_j_mol_K) * (1.0 / Tk_K - 1.0 / Tp_K)
    return P0_kpa * math.exp(exponent)


def eta_from_table_1(air_speed_m_s: float, air_temp_c: float) -> float:
    """
    Коэффициент η по таблице №1.

    В текущей версии — ПРИБЛИЖЁННАЯ реализация:
    - значения таблицы зашиты в код,
    - применяется простая двулинейная интерполяция по скорости и температуре,
      с правилами "обрезки" из методики (выше 1 м/с => как при 1 м/с; выше 35°C => как при 35°C; ниже 10°C => как при 10°C).

    Таблица (по присланному фрагменту):
      Скорость (м/с) \ Температура (°C): 10, 15, 20, 30, 35
      0.0 : 1.0, 1.0, 1.0, 1.0, 1.0
      0.1 : 3.0, 2.6, 2.4, 1.8, 1.6
      0.2 : 4.6, 3.8, 3.5, 2.4, 2.3
      0.5 : 6.6, 5.7, 5.4, 3.6, 3.2
      1.0 : 10.0, 8.7, 7.7, 5.6, 4.6
    """
    # Ограничения согласно тексту под таблицей
    v = max(0.0, min(air_speed_m_s, 1.0))
    t = air_temp_c
    if t < 10.0:
        t = 10.0
    if t > 35.0:
        t = 35.0

    speeds = [0.0, 0.1, 0.2, 0.5, 1.0]
    temps = [10.0, 15.0, 20.0, 30.0, 35.0]
    table = {
        0.0: [1.0, 1.0, 1.0, 1.0, 1.0],
        0.1: [3.0, 2.6, 2.4, 1.8, 1.6],
        0.2: [4.6, 3.8, 3.5, 2.4, 2.3],
        0.5: [6.6, 5.7, 5.4, 3.6, 3.2],
        1.0: [10.0, 8.7, 7.7, 5.6, 4.6],
    }

    def lerp(a: float, b: float, x: float) -> float:
        return a + (b - a) * x

    # Найдём индексы по скорости
    for i in range(len(speeds) - 1):
        if speeds[i] <= v <= speeds[i + 1]:
            v0, v1 = speeds[i], speeds[i + 1]
            break
    else:
        v0, v1 = speeds[-2], speeds[-1]

    # Найдём индексы по температуре
    for j in range(len(temps) - 1):
        if temps[j] <= t <= temps[j + 1]:
            t0, t1 = temps[j], temps[j + 1]
            break
    else:
        t0, t1 = temps[-2], temps[-1]

    # Нормированные координаты
    xv = 0.0 if v1 == v0 else (v - v0) / (v1 - v0)
    xt = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)

    # Значения в узлах
    f_v0 = table[v0]
    f_v1 = table[v1]

    # Интерполяция по температуре для каждой скорости
    y00 = lerp(f_v0[temps.index(t0)], f_v0[temps.index(t1)], xt)
    y10 = lerp(f_v1[temps.index(t0)], f_v1[temps.index(t1)], xt)

    # Интерполяция по скорости
    return lerp(y00, y10, xv)


def spill_energy_kj(data: SpillEvaporationData) -> tuple[float, float, float, float]:
    """
    Расчёт п. 1.6.

    Возвращает кортеж:
        (E4_kj, G_total_kg, G4_kg, G5_kg)

    где:
        E4_kj       — энергия сгорания ПГФ от пролива, кДж
        G_total_kg  — суммарная масса парогазовой фазы GΣ'', кг
        G4_kg       — вклад от теплопередачи от подстилающей поверхности, кг
        G5_kg       — вклад от испарения в атмосферу, кг
    """
    _require_positive("r", data.r)
    _require_positive("Fp_m2", data.Fp_m2)
    _require_non_negative("tau_s", data.tau_s)
    _require_positive("q_kj_kg", data.q_kj_kg)

    # ε = sqrt(λ ρ c)
    epsilon = (data.lambda_W * data.rho_kg_m3 * data.c) ** 0.5

    # G4'' (формула 13)
    # Физический смысл: тепло передаётся ОТ поверхности К жидкости.
    # Если поверхность холоднее температуры кипения (T0 <= Tk),
    # вклад теплопередачи в испарение не должен давать отрицательную массу.
    deltaT = data.T0_K - data.Tk_K
    if deltaT <= 0:
        G4 = 0.0
    else:
        G4 = (
                2 * deltaT / data.r
                * (epsilon / math.sqrt(math.pi))
                * data.Fp_m2
                * math.sqrt(data.tau_s)
        )

    # mн = 10^-6 * η * Pн / sqrt(M)
    eta = data.eta
    if getattr(data, "use_table_eta", False):
        eta = eta_from_table_1(data.air_speed_m_s, data.air_temp_c)

    Pn_kpa = data.Pn_kpa
    if getattr(data, "use_calc_Pn", False) and getattr(data, "r_j_mol", None) is not None:
        Tp = data.Tp_K
        if Tp is None:
            Tp = max(data.T0_K, data.Tk_K)
        Pn_kpa = saturated_vapor_pressure_kpa(data.P0_kpa, data.r_j_mol, data.R_j_mol_K, data.Tk_K, Tp)

    m_n = 1e-6 * eta * math.sqrt(data.M) * Pn_kpa

    # G5''
    G5 = m_n * data.Fp_m2 * data.tau_s

    G_total = G4 + G5
    if G_total < 0:
        G_total = 0.0

    E4 = G_total * data.q_kj_kg

    return E4, G_total, G4, G5


# ======================================================================
# ТРАССИРОВКА РАСЧЁТА (подробный вывод промежуточных величин)
# ======================================================================

@dataclass
class Trace:
    """
    Накопитель строк трассировки.

    Идея:
    - функции расчёта могут добавлять в Trace пары "имя = значение (ед.)"
    - затем весь Trace печатается одним блоком

    Это удобно для проверки "цепочки расчётов" и сопоставления с методикой.
    """
    lines: List[str]

    def add(self, name: str, value, unit: str = "", comment: str = "") -> None:
        unit_str = f" {unit}" if unit else ""
        comment_str = f" — {comment}" if comment else ""
        self.lines.append(f"{name} = {value}{unit_str}{comment_str}")

    def add_sep(self, title: str) -> None:
        self.lines.append("")
        self.lines.append(f"--- {title} ---")

    def dump(self) -> str:
        return "\n".join(self.lines)


# ======================================================================
# ЕДИНЫЙ БЛОК ИСХОДНЫХ ДАННЫХ (все пункты в одной структуре)
# ======================================================================

@dataclass(frozen=True)
class UnifiedInputData:
    """
    Единый контейнер исходных данных для всех реализованных пунктов.

    Поля:
    - block          : данные п.1.1
    - flows_gas      : список потоков ПГФ от смежных блоков (п.1.2)
    - overheated_liq : перегретая ЖФ внутри блока (п.1.3) — может быть None
    - flows_liq      : список потоков перегретой ЖФ от смежных блоков (п.1.3)
    - spill          : данные пролива ЖФ на твёрдую поверхность (п.1.6) — может быть None
    """
    block: BlockData
    flows_gas: List[FlowData]
    overheated_liq: OverheatedLiquidInBlock | None
    flows_liq: List[LiquidFlowData]
    spill: SpillEvaporationData | None

    def pretty(self) -> str:
        """
        Текстовый вывод исходных данных (для протокола расчёта).
        """
        lines: List[str] = []
        lines.append("=== ИСХОДНЫЕ ДАННЫЕ (единый блок) ===")

        b = self.block
        lines.append("[П.1.1] ПГФ в блоке:")
        lines.append(f"  P = {b.P_mpa} МПа (абс.)")
        lines.append(f"  P0 = {b.P0_mpa} МПа (абс.)")
        lines.append(f"  V' = {b.V_m3} м³")
        lines.append(f"  T1 = {b.T1_K} К")
        lines.append(f"  ρ = {b.rho_kg_m3} кг/м³")
        lines.append(f"  k = {b.k}")
        lines.append(f"  q = {b.q_kj_kg} кДж/кг")

        lines.append("[П.1.2] Потоки ПГФ от смежных блоков:")
        if self.flows_gas:
            for i, f in enumerate(self.flows_gas, start=1):
                lines.append(
                    f"  Поток {i}: Pi={f.Pi_mpa} МПа, ρ={f.rho_kg_m3} кг/м³, "
                    f"S={f.S_m2} м², τ={f.tau_s} с, k={f.k}, q={f.q_kj_kg} кДж/кг"
                )
        else:
            lines.append("  (нет потоков)")

        lines.append("[П.1.3] Перегретая ЖФ:")
        if self.overheated_liq is None:
            lines.append("  В блоке: (нет)")
        else:
            o = self.overheated_liq
            lines.append(
                f"  В блоке: G1''={o.G_kg} кг, q={o.q_kj_kg} кДж/кг, c1={o.c1}, θ={o.theta_s} с, r={o.r_m} м"
            )

        if self.flows_liq:
            lines.append("  Потоки ЖФ от смежных блоков:")
            for i, lf in enumerate(self.flows_liq, start=1):
                lines.append(
                    f"    Поток {i}: ρ={lf.rho_kg_m3} кг/м³, S={lf.S_m2} м², τ={lf.tau_s} с, "
                    f"ΔP={lf.deltaP_mpa} МПа, μ={lf.mu}, q={lf.q_kj_kg} кДж/кг, c1={lf.c1}, θ={lf.theta_s} с, r={lf.r_m} м"
                )
        else:
            lines.append("  Потоки ЖФ от смежных блоков: (нет)")

        lines.append("[П.1.6] Пролив ЖФ на твёрдую поверхность:")
        if self.spill is None:
            lines.append("  (не рассчитывается)")
        else:
            s = self.spill
            lines.append(f"  T0={s.T0_K} К, Tk={s.Tk_K} К, r={s.r}, λ={s.lambda_W}, ρ={s.rho_kg_m3}, c={s.c}")
            lines.append(
                f"  Fп={s.Fp_m2} м², τи={s.tau_s} с, η={s.eta}, Pн={s.Pn_kpa} кПа, M={s.M}, q={s.q_kj_kg} кДж/кг")
            if getattr(s, 'use_table_eta', False):
                lines.append(f"  (η по таблице №1) v_воздуха={s.air_speed_m_s} м/с, t_воздуха={s.air_temp_c} °C")
            if getattr(s, 'use_calc_Pn', False):
                lines.append(
                    f"  (Pн по формуле) P0={s.P0_kpa} кПа, R={s.R_j_mol_K} Дж/(моль·К), r={s.r_j_mol} Дж/моль, Tp={s.Tp_K}")

        return "\n".join(lines)


# ======================================================================
# ДЕТАЛЬНЫЕ РАСЧЁТЫ С ТРАССИРОВКОЙ (проверка всей цепочки)
# ======================================================================

def energy_in_block_kj_detailed(data: BlockData, tr: Trace) -> tuple[float, float, float]:
    """
    П.1.1 с подробной трассировкой всех промежуточных величин.
    """
    tr.add_sep("П.1.1 — ПГФ в блоке")

    P = data.P_mpa
    P0 = data.P0_mpa
    V = data.V_m3
    k = data.k

    tr.add("P", P, "МПа", "абсолютное давление в блоке")
    tr.add("P0", P0, "МПа", "атмосферное/опорное абсолютное давление")
    tr.add("V'", V, "м³", "объём ПГФ в блоке")
    tr.add("k", k, "", "показатель адиабаты")

    P_excess = P - P0
    PV = P * V
    tr.add("Pизб", P_excess, "МПа", "избыточное давление")
    tr.add("P*V'", PV, "МПа·м³", "проверка малости для A")

    # β1
    b1 = beta1(P, P0, k)
    tr.add("β1", b1, "", "коэффициент для A = β1·P·V'")

    # A
    if P_excess < 0.07 and PV < 0.02:
        A = 0.0
        tr.add("A", A, "кДж", "не учитываем по условию (малые Pизб и PV)")
    else:
        A = b1 * PV * 1000.0
        tr.add("A", A, "кДж", "1 МПа·м³ = 1000 кДж")

    # Температура/плотность/приведённый объём и масса
    T1 = data.T1_K
    rho = data.rho_kg_m3
    tr.add("T1", T1, "К", "температура в блоке")
    tr.add("ρ", rho, "кг/м³", "плотность при P и T1")

    T = T1 * (P0 / P) ** ((k - 1.0) / k)
    tr.add("T", T, "К", "после адиабатического расширения")

    rho0 = rho * (P0 / P) ** (1.0 / k)
    tr.add("ρ0'", rho0, "кг/м³", "после расширения")

    V0 = (P / P0) * (V / T1) * T
    tr.add("V0'", V0, "м³", "приведённый объём")

    G1 = V0 * rho0
    tr.add("G1'", G1, "кг", "масса ПГФ для E1'")

    # Контрольная проверка: при определённой трактовке ρ формулы могут сократиться,
    # и получится тождество G1' = V' * ρ.
    # Если вы задаёте ρ как плотность при P и T1 (внутри блока),
    # то это равенство будет выполняться почти точно.
    # Если же по методике ρ должна быть при других условиях (например, при опорных/нормальных),
    # тождество нарушится — и это будет индикатором корректной трактовки входных данных.
    G1_check = data.V_m3 * data.rho_kg_m3
    tr.add("G1_check = V'·ρ", G1_check, "кг", "контроль: V' * ρ")
    rel = abs(G1 - G1_check) / max(abs(G1_check), 1e-12)
    tr.add("rel_err", rel, "", "относит. расхождение G1' и V'·ρ")
    if rel < 1e-6:
        tr.add("ПРИМЕЧАНИЕ", "G1'≈V'·ρ", "", "проверьте, что ρ задана в тех условиях, которые подразумевает методика")

    q = data.q_kj_kg
    tr.add("q", q, "кДж/кг", "удельная теплота сгорания")

    E_comb = G1 * q
    tr.add("G1'*q", E_comb, "кДж", "энергия сгорания массы G1'")

    E1 = E_comb + A
    tr.add("E1'", E1, "кДж", "итог п.1.1")

    return E1, G1, A


def energy_from_adjacent_blocks_kj_detailed(flows: List[FlowData], P0_mpa: float, tr: Trace) -> tuple[
    float, List[float]]:
    """
    П.1.2 с подробной трассировкой.
    """
    tr.add_sep("П.1.2 — Потоки ПГФ от смежных блоков")
    tr.add("P0", P0_mpa, "МПа", "опорное абсолютное давление")

    total = 0.0
    masses: List[float] = []

    for i, flow in enumerate(flows, start=1):
        tr.add_sep(f"П.1.2 — Поток {i}")

        Pi = flow.Pi_mpa
        rho = flow.rho_kg_m3
        S = flow.S_m2
        tau = flow.tau_s
        k = flow.k
        q = flow.q_kj_kg

        tr.add("Pi", Pi, "МПа", "абсолютное давление потока")
        tr.add("ρi'", rho, "кг/м³", "плотность потока")
        tr.add("Si'", S, "м²", "площадь сечения")
        tr.add("τi", tau, "с", "время поступления")
        tr.add("k", k, "", "показатель адиабаты")
        tr.add("qi'", q, "кДж/кг", "теплота сгорания")

        P_excess = Pi - P0_mpa
        tr.add("Pизб", P_excess, "МПа", "для выбора формулы скорости")

        Pi_pa = Pi * 1_000_000.0
        tr.add("Pi", Pi_pa, "Па", "перевод: 1 МПа = 1e6 Па")

        if P_excess <= 0.07:
            w = ((2.0 * k / (k + 1.0)) * (Pi_pa / rho)) ** 0.5
            tr.add("wi'", w, "м/с", "упрощённая формула (Pизб <= 0.07 МПа)")
        else:
            P0_pa = P0_mpa * 1_000_000.0
            term = 1.0 - (P0_pa / Pi_pa) ** ((k - 1.0) / k)
            tr.add("term", term, "", "[1 - (P0/P)^((k-1)/k)]")
            w = ((2.0 * k / (k - 1.0)) * (Pi_pa / rho) * term) ** 0.5
            tr.add("wi'", w, "м/с", "общая формула")

        Gi = rho * w * S * tau
        tr.add("Gi'", Gi, "кг", "масса потока")
        masses.append(Gi)

        Ei = Gi * q
        tr.add("Gi'*qi'", Ei, "кДж", "энергия потока")
        total += Ei

    tr.add_sep("Итог п.1.2")
    tr.add("E2'", total, "кДж", "сумма по потокам")

    return total, masses


def energy_from_overheated_liquid_kj_detailed(
        in_block: OverheatedLiquidInBlock | None,
        incoming_flows: List[LiquidFlowData] | None,
        tr: Trace
) -> tuple[float, float, List[float]]:
    """
    П.1.3 с подробной трассировкой.
    """
    tr.add_sep("П.1.3 — Перегретая ЖФ")

    total = 0.0
    G1 = 0.0
    Gi_list: List[float] = []

    def frac(c1: float, theta: float, r: float) -> float:
        f = 1.0 - math.exp(-c1 * theta / r)
        return f

    # В блоке
    if in_block is not None:
        tr.add_sep("П.1.3 — Перегретая ЖФ в блоке")
        tr.add("G1''", in_block.G_kg, "кг")
        tr.add("q1", in_block.q_kj_kg, "кДж/кг")
        tr.add("c1", in_block.c1, "")
        tr.add("θ", in_block.theta_s, "с")
        tr.add("r1", in_block.r_m, "м")

        f1 = frac(in_block.c1, in_block.theta_s, in_block.r_m)
        tr.add("f1", f1, "", "f=1-exp(-c1*θ/r)")

        G1 = in_block.G_kg
        E1 = G1 * f1 * in_block.q_kj_kg
        tr.add("E_block", E1, "кДж", "вклад от ЖФ в блоке")
        total += E1

    # Поступившие ЖФ
    if incoming_flows:
        for i, flow in enumerate(incoming_flows, start=1):
            tr.add_sep(f"П.1.3 — Поток ЖФ {i}")
            tr.add("ρi''", flow.rho_kg_m3, "кг/м³")
            tr.add("Si''", flow.S_m2, "м²")
            tr.add("τi", flow.tau_s, "с")
            tr.add("ΔP", flow.deltaP_mpa, "МПа")
            tr.add("μ", flow.mu, "")
            tr.add("qi", flow.q_kj_kg, "кДж/кг")
            tr.add("c1", flow.c1, "")
            tr.add("θ", flow.theta_s, "с")
            tr.add("ri", flow.r_m, "м")

            deltaP_pa = flow.deltaP_mpa * 1_000_000.0
            tr.add("ΔP", deltaP_pa, "Па", "перевод: 1 МПа = 1e6 Па")

            w = flow.mu * (2.0 * deltaP_pa / flow.rho_kg_m3) ** 0.5
            tr.add("wi''", w, "м/с", "w'' = μ*sqrt(2ΔP/ρ)")

            Gi = flow.rho_kg_m3 * w * flow.S_m2 * flow.tau_s
            tr.add("Gi''", Gi, "кг", "масса ЖФ, поступившая за τi")
            Gi_list.append(Gi)

            fi = frac(flow.c1, flow.theta_s, flow.r_m)
            tr.add("fi", fi, "", "f=1-exp(-c1*θ/r)")

            Ei = Gi * fi * flow.q_kj_kg
            tr.add("Ei", Ei, "кДж", "вклад потока ЖФ")
            total += Ei

    tr.add_sep("Итог п.1.3")
    tr.add("E3'", total, "кДж")

    return total, G1, Gi_list


def spill_energy_kj_detailed(data: SpillEvaporationData, tr: Trace) -> tuple[float, float, float, float]:
    """
    П.1.6 с подробной трассировкой.

    Здесь особенно важно проследить цепочку:
      mн (формула 14) -> G5'' -> GΣ'' -> E4'
    """
    tr.add_sep("П.1.6 — Пролив ЖФ на твёрдую поверхность")

    tr.add("T0", data.T0_K, "К", "температура поверхности")
    tr.add("Tk", data.Tk_K, "К", "температура кипения жидкости")
    tr.add("r", data.r, "Дж/кг", "теплота фазового перехода")
    tr.add("λ", data.lambda_W, "Вт/(м·К)", "теплопроводность")
    tr.add("ρс", data.rho_kg_m3, "кг/м³", "плотность материала поверхности")
    tr.add("c", data.c, "Дж/(кг·К)", "удельная теплоёмкость")
    tr.add("Fп", data.Fp_m2, "м²", "площадь пролива")
    tr.add("τи", data.tau_s, "с", "время испарения/контакта")
    eta = data.eta
    if getattr(data, "use_table_eta", False):
        eta = eta_from_table_1(data.air_speed_m_s, data.air_temp_c)
        tr.add("η", eta, "", "взято по таблице №1 (интерполяция)")
        tr.add("v_воздуха", data.air_speed_m_s, "м/с")
        tr.add("t_воздуха", data.air_temp_c, "°C")
    else:
        tr.add("η", eta, "", "задано вручную")

    Pn_kpa = data.Pn_kpa
    if getattr(data, "use_calc_Pn", False) and getattr(data, "r_j_mol", None) is not None:
        Tp = data.Tp_K
        if Tp is None:
            # Если пользователь не задал Tp, берём грубую оценку: максимум из температур в данных
            Tp = max(data.T0_K, data.Tk_K)
        Pn_kpa = saturated_vapor_pressure_kpa(data.P0_kpa, data.r_j_mol, data.R_j_mol_K, data.Tk_K, Tp)
        tr.add("Tp", Tp, "К", "расчётная температура для Pн")
        tr.add("P0", data.P0_kpa, "кПа", "база для Pн")
        tr.add("r", data.r_j_mol, "Дж/моль", "для формулы Pн")
        tr.add("R", data.R_j_mol_K, "Дж/(моль·К)")
        tr.add("Pн", Pn_kpa, "кПа", "рассчитано по формуле насыщенного пара")
    else:
        tr.add("Pн", Pn_kpa, "кПа", "задано вручную")
    tr.add("M", data.M, "кг/кмоль", "молярная масса")
    tr.add("q", data.q_kj_kg, "кДж/кг", "теплота сгорания")

    # ε = sqrt(λ ρ c)
    epsilon = (data.lambda_W * data.rho_kg_m3 * data.c) ** 0.5
    tr.add("ε", epsilon, "Дж/(м²·К·√с)", "sqrt(λ·ρ·c)")

    # G4'' (формула 13)
    deltaT = data.T0_K - data.Tk_K
    tr.add("ΔT", deltaT, "К", "T0 - Tk (если <=0, теплопередача не испаряет)")
    if deltaT <= 0:
        G4 = 0.0
        tr.add("G4''", G4, "кг", "T0<=Tk => отрицательный вклад не допускаем, принимаем 0")
    else:
        G4 = (
                2.0 * deltaT / data.r
                * (epsilon / math.sqrt(math.pi))
                * data.Fp_m2
                * math.sqrt(data.tau_s)
        )
        tr.add("G4''", G4, "кг", "вклад от теплопередачи поверхности")

    # mн (формула 14)
    m_n = 1e-6 * eta * Pn_kpa * (data.M ** 0.5)
    tr.add("mн", m_n, "кг/(м²·с)", "10^-6 * η * Pн * sqrt(M)")

    # G5''
    G5 = m_n * data.Fp_m2 * data.tau_s
    tr.add("G5''", G5, "кг", "вклад от испарения в атмосферу")

    Gsum = G4 + G5
    if Gsum < 0:
        # На практике это не должно происходить (масса не бывает отрицательной).
        # Оставляем защиту на случай некорректного набора исходных данных.
        tr.add("ПРЕДУПРЕЖДЕНИЕ", "GΣ''<0", "", "масса не может быть отрицательной; принимаем 0")
        Gsum = 0.0
    tr.add("GΣ''", Gsum, "кг", "суммарная масса парогазовой фазы")

    E4 = Gsum * data.q_kj_kg
    tr.add("E4'", E4, "кДж", "энергия сгорания ПГФ от пролива")

    return E4, Gsum, G4, G5


def calculate_all_energies_detailed(inp: UnifiedInputData) -> dict:
    """
    Полная проверка цепочки расчётов с подробным протоколом.

    Возвращает словарь:
      - 'trace' : текст трассировки
      - 'results': численные результаты (E1, E2, E3, E4, E_sum и др.)
    """
    tr = Trace(lines=[])

    # Печатаем исходные данные как часть протокола
    tr.add_sep("Исходные данные")
    for line in inp.pretty().splitlines():
        tr.lines.append(line)

    # 1.1
    E1, G1, A = energy_in_block_kj_detailed(inp.block, tr)

    # 1.2
    E2, masses_gas = energy_from_adjacent_blocks_kj_detailed(inp.flows_gas, inp.block.P0_mpa,
                                                             tr) if inp.flows_gas else (0.0, [])

    # 1.3
    E3, G1_liq, masses_liq = energy_from_overheated_liquid_kj_detailed(inp.overheated_liq, inp.flows_liq, tr)

    # 1.6
    if inp.spill is not None:
        E4, Gsum, G4, G5 = spill_energy_kj_detailed(inp.spill, tr)
    else:
        E4, Gsum, G4, G5 = 0.0, 0.0, 0.0, 0.0
        tr.add_sep("П.1.6 — Пролив ЖФ")
        tr.lines.append("(не рассчитывается)")

    E_sum = E1 + E2 + E3 + E4
    tr.add_sep("ИТОГ")
    tr.add("E_sum", E_sum, "кДж", "E1'+E2'+E3'+E4' (реализованные пункты)")

    # ==================================================================
    # П.2 — Категория взрывоопасности
    # ==================================================================
    tr.add_sep("П.2 — Категория взрывоопасности технологического блока")

    # 2.1 Приведённая масса (формула 17)
    # m = E / (4.6 * 10^4)
    m_pr = E_sum / (4.6 * 10 ** 4)
    tr.add("m", m_pr, "кг", "приведённая масса (E / 4.6·10^4)")

    # 2.2 Относительный энергетический потенциал (формула 18)
    # Qв = (1 / 16.534) * E^(1/3)
    if E_sum > 0:
        Qv = (1.0 / 16.534) * (E_sum ** (1.0 / 3.0))
    else:
        Qv = 0.0

    tr.add("Qв", Qv, "", "(1/16.534)*E^(1/3)")

    # Определение категории
    if Qv > 37 and m_pr > 5000:
        category = "I"
    elif 27 <= Qv <= 37 and 2000 <= m_pr <= 5000:
        category = "II"
    else:
        category = "III"

    tr.add("Категория", category, "", "по таблице №3")

    results = {
        "E1_kj": E1, "G1_kg": G1, "A_kj": A,
        "E2_kj": E2, "masses_gas_kg": masses_gas,
        "E3_kj": E3, "G1_liquid_kg": G1_liq, "masses_liquid_kg": masses_liq,
        "E4_kj": E4, "Gsum_spill_kg": Gsum, "G4_spill_kg": G4, "G5_spill_kg": G5,
        "E_sum_kj": E_sum,
    }
    results.update({
        "m_pr_kg": m_pr,
        "Qv": Qv,
        "category": category,
    })

    return {"trace": tr.dump(), "results": results}


# ======================================================================
# ОБЩАЯ ФУНКЦИЯ-ОБЁРТКА (необязательно, но удобно в практике)
# ======================================================================

def calculate_all_energies(
        block: BlockData,
        flows_gas: List[FlowData] | None = None,
        overheated_in_block: OverheatedLiquidInBlock | None = None,
        flows_liquid: List[LiquidFlowData] | None = None,
        spill: SpillEvaporationData | None = None,
) -> dict:
    """
    Унифицированный расчёт всех реализованных пунктов методики.

    Возвращает словарь с ключами:
        E1_kj, E2_kj, E3_kj, E4_kj, E_sum_kj
    а также диагностическими величинами (массы и т.п.).

    Примечание:
    - Если какой-то набор данных не передан (None), соответствующий вклад считается нулевым.
    - E4 соответствует п. 1.6 (пролив ЖФ на твёрдую поверхность).
    """
    result: dict = {}

    # 1.1
    E1, G1, A = energy_in_block_kj(block)
    result["E1_kj"] = E1
    result["G1_kg"] = G1
    result["A_kj"] = A

    # 1.2
    if flows_gas:
        E2, masses_g = energy_from_adjacent_blocks_kj(flows_gas, P0_mpa=block.P0_mpa)
    else:
        E2, masses_g = 0.0, []
    result["E2_kj"] = E2
    result["masses_gas_kg"] = masses_g

    # 1.3
    E3, G1_liq, Gi_liq = energy_from_overheated_liquid_kj(overheated_in_block, flows_liquid)
    result["E3_kj"] = E3
    result["G1_liquid_kg"] = G1_liq
    result["masses_liquid_kg"] = Gi_liq

    # 1.6
    if spill is not None:
        E4, Gsum, G4, G5 = spill_energy_kj(spill)
    else:
        E4, Gsum, G4, G5 = 0.0, 0.0, 0.0, 0.0
    result["E4_kj"] = E4
    result["Gsum_spill_kg"] = Gsum
    result["G4_spill_kg"] = G4
    result["G5_spill_kg"] = G5

    # Сумма
    result["E_sum_kj"] = E1 + E2 + E3 + E4

    return result


# ======================================================================
# ПРИМЕР ЗАПУСКА ПРОГРАММЫ (ОСОБОЕ ВНИМАНИЕ)
# ======================================================================

if __name__ == "__main__":
    """
    Пример использования программы.

    Цель примера:
    1) показать ЕДИНЫЙ блок исходных данных (UnifiedInputData)
    2) вывести исходные данные текстом (для протокола)
    3) выполнить проверку всей цепочки расчётов с подробным выводом
       промежуточных величин (трассировка)
    """

    # ------------------------------------------------------------------
    # ЕДИНЫЙ БЛОК ИСХОДНЫХ ДАННЫХ
    # ------------------------------------------------------------------

    # (п. 1.1) ПГФ в блоке
    block = BlockData(
        P_mpa=0.4,  # абсолютное давление в блоке, МПа
        P0_mpa=0.1,  # атмосферное/опорное давление, МПа
        V_m3=20,  # объём ПГФ в блоке V', м³
        T1_K=40 + 273.15,  # температура в блоке T1, К
        rho_kg_m3=2.7,  # плотность ПГФ при P и T1, кг/м³
        k=1.3,  # показатель адиабаты
        q_kj_kg=41600.0  # удельная теплота сгорания, кДж/кг
    )

    # (п. 1.2) Потоки ПГФ от смежных блоков
    flows_gas = [
        # FlowData(Pi_mpa=0.9, rho_kg_m3=6.0, S_m2=0.010, tau_s=30.0, k=1.3, q_kj_kg=45000.0),
        # FlowData(Pi_mpa=0.5, rho_kg_m3=4.5, S_m2=0.008, tau_s=20.0, k=1.3, q_kj_kg=44000.0),
    ]

    # (п. 1.3) Перегретая ЖФ в блоке
    overheated_liq = OverheatedLiquidInBlock(G_kg=0.0, q_kj_kg=45000.0, c1=0.15, theta_s=60.0, r_m=1.0)

    # (п. 1.3) Потоки перегретой ЖФ от смежных блоков
    flows_liq = [
        LiquidFlowData(
            rho_kg_m3=800.0, S_m2=0, tau_s=40.0,
            deltaP_mpa=0.2, mu=0.6,
            q_kj_kg=45000.0,
            c1=0.15, theta_s=60.0, r_m=1.2
        )
    ]

    # (п. 1.6) Пролив ЖФ на твёрдую поверхность
    spill = SpillEvaporationData(
        T0_K=25 + 273.15,
        Tk_K=40 + 273.15,
        r=2.0e5,
        lambda_W=1.2,
        rho_kg_m3=1800.0,
        c=900.0,
        Fp_m2=560.0,
        tau_s=3600.0,
        eta=1,
        Pn_kpa=65,  # r_j_mol - задан
        M=310.0,
        q_kj_kg=41600.0,
        air_speed_m_s=1,  # пример: скорость воздуха над зеркалом
        air_temp_c=20.0,  # пример: температура воздуха для η
        use_table_eta=False,  # True => η возьмётся по табл. №1
        use_calc_Pn=False,  # True и r_j_mol задан => Pн посчитаем по формуле
        r_j_mol=20000,  # если хотите считать Pн: задайте r в Дж/моль
        Tp_K=None  # если хотите считать Pн: задайте Tp (К) или оставьте None
    )

    # Собираем всё в единый объект
    inp = UnifiedInputData(
        block=block,
        flows_gas=flows_gas,
        overheated_liq=overheated_liq,
        flows_liq=flows_liq,
        spill=spill
    )

    # ------------------------------------------------------------------
    # ПОДРОБНЫЙ ПРОТОКОЛ РАСЧЁТА (включая промежуточные величины)
    # ------------------------------------------------------------------
    out = calculate_all_energies_detailed(inp)

    print(out["trace"])

    # При необходимости можно отдельно использовать численные результаты:
    results = out["results"]

    print("\n=== КРАТКИЙ ИТОГ (числа) ===")
    print(f"E1' = {results['E1_kj']:.2f} кДж")
    print(f"E2' = {results['E2_kj']:.2f} кДж")
    print(f"E3' = {results['E3_kj']:.2f} кДж")
    print(f"E4' = {results['E4_kj']:.2f} кДж")
    print(f"E_sum = {results['E_sum_kj']:.2f} кДж")
    print("\n=== ПОКАЗАТЕЛИ КАТЕГОРИИ ===")
    print(f"m = {results['m_pr_kg']:.2f} кг")
    print(f"Qв = {results['Qv']:.2f}")
    print(f"Категория блока = {results['category']}")
