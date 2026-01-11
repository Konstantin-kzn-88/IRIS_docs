# -*- coding: utf-8 -*-
"""
FN / FG диаграммы (ступенчатые):
- Горизонтальные участки: сплошные линии с точками
- Вертикальные переходы: штриховые линии с точками
- От последней точки: штриховая вертикаль вниз до 0

Способ приёма данных и вывода: из charts.py (словари -> точки, сохранение в PNG)
Способ отрисовки: из get_chart.py (логика построения линий)

Файл предназначен для headless-генерации PNG (в отчёт Word).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict, Any

import matplotlib

matplotlib.use("Agg")  # ВАЖНО: без GUI/backends

import matplotlib.pyplot as plt
import numpy as np

Point = Tuple[float, float]


def _safe_float(x) -> float | None:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


# ---------------------------
# F/N
# ---------------------------

def build_fn_points(rows: List[Dict[str, Any]]) -> List[Point]:
    """
    rows: dict with keys:
      - fatalities_count
      - scenario_frequency
    Возвращает точки (N, F(N)), где F(N)=Σfreq(fatalities>=N).
    """
    freq_by_n: Dict[int, float] = {}

    for r in rows:
        n_raw = r.get("fatalities_count")
        f_raw = r.get("scenario_frequency")
        f = _safe_float(f_raw)
        if n_raw is None or f is None:
            continue
        try:
            n = int(n_raw)
        except Exception:
            continue
        freq_by_n[n] = freq_by_n.get(n, 0.0) + f

    if not freq_by_n:
        return []

    points: List[Point] = []
    for n in sorted(freq_by_n.keys()):
        f_sum = sum(v for k, v in freq_by_n.items() if k >= n)
        points.append((float(n), float(f_sum)))

    # Часто нужно начинать с N=0 как F(0)=F(1) (визуально как в примере)
    if points and points[0][0] > 0:
        points = [(0.0, points[0][1])] + points

    # убираем нулевые/отрицательные частоты (на лог шкале нельзя)
    points = [(x, y) for x, y in points if y > 0]
    return points


def save_fn_chart(points: List[Point], path: Path) -> None:
    """
    Строит и сохраняет F/N диаграмму.

    :param points: список точек [(N1, F1), (N2, F2), ...]
    :param path: путь для сохранения PNG
    """
    if not points:
        return

    # Преобразуем точки в формат для отрисовки в стиле get_chart.py
    # Убираем точку с N=0 для построения, но используем её значение
    plot_points = [(x, y) for x, y in points if x > 0]

    if len(plot_points) < 1:
        return

    people = [int(p[0]) for p in plot_points]
    probability = [p[1] for p in plot_points]

    # для сплошных линий (горизонтальные участки)
    chart_line_x = []
    chart_line_y = []
    for idx, n in enumerate(people):
        chart_line_x.extend([n - 1, n, n, n])
        chart_line_y.extend([probability[idx], probability[idx], None, None])

    # для пунктирных линий (вертикальные переходы)
    chart_dot_line_x = []
    chart_dot_line_y = []
    for idx, n in enumerate(people):
        if idx == len(people) - 1:
            # Последняя вертикаль вниз
            chart_dot_line_x.extend([n, n])
            chart_dot_line_y.extend([probability[idx], 0])
            break
        chart_dot_line_x.extend([n, n])
        chart_dot_line_y.extend([probability[idx], probability[idx + 1]])

    # Отрисовка графика
    fig = plt.figure()
    plt.semilogy(chart_line_x, chart_line_y, color='b', linestyle='-', marker='.')
    plt.semilogy(chart_dot_line_x, chart_dot_line_y, color='b', linestyle='--', marker='.')
    plt.xticks(ticks=people)
    plt.title('F/N - диаграмма')
    plt.xlabel('Количество погибших, чел')
    plt.ylabel('Вероятность, 1/год')
    plt.grid(True)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------
# F/G
# ---------------------------

def build_fg_points(rows: List[Dict[str, Any]]) -> List[Point]:
    """
    rows: dict with keys:
      - total_damage (тыс. руб)
      - scenario_frequency
    Возвращает точки (G, F(G)), где:
      G = ущерб в млн руб,
      F(G)=Σfreq(total_damage>=G).
    """
    freq_by_g: Dict[float, float] = {}

    for r in rows:
        g_raw = r.get("total_damage")
        f_raw = r.get("scenario_frequency")
        g = _safe_float(g_raw)
        f = _safe_float(f_raw)
        if g is None or f is None:
            continue

        # тыс.руб -> млн.руб
        g_mln = g / 1000.0

        # Упорядочивание/слияние близких значений (чтобы не было "дрожания" из-за float)
        g_key = round(g_mln, 6)
        freq_by_g[g_key] = freq_by_g.get(g_key, 0.0) + f

    if not freq_by_g:
        return []

    points: List[Point] = []
    g_sorted = sorted(freq_by_g.keys())
    for g in g_sorted:
        f_sum = sum(v for k, v in freq_by_g.items() if k >= g)
        points.append((float(g), float(f_sum)))

    # старт с G=0 как F(0)=F(minG)
    if points and points[0][0] > 0:
        points = [(0.0, points[0][1])] + points

    points = [(x, y) for x, y in points if y > 0]
    return points


def save_fg_chart(points: List[Point], path: Path) -> None:
    """
    Строит и сохраняет F/G диаграмму.

    :param points: список точек [(G1, F1), (G2, F2), ...] где G в млн.руб
    :param path: путь для сохранения PNG
    """
    if not points:
        return

    # Убираем точку с G=0 для построения
    plot_points = [(x, y) for x, y in points if x > 0]

    if len(plot_points) < 1:
        return

    damage = [p[0] for p in plot_points]
    probability = [p[1] for p in plot_points]

    # для сплошных линий (горизонтальные участки)
    chart_line_x = []
    chart_line_y = []
    for idx, g in enumerate(damage):
        if idx == 0:
            # Первый участок начинается с 0
            chart_line_x.extend([0, g, g, g])
            chart_line_y.extend([probability[idx], probability[idx], None, None])
        elif idx == len(damage) - 1:
            # Последний участок
            chart_line_x.extend([damage[idx - 1], damage[idx - 1], g, g])
            chart_line_y.extend([probability[idx], probability[idx],
                                 probability[idx], probability[idx]])
            break
        else:
            chart_line_x.extend([damage[idx - 1], g, g, g])
            chart_line_y.extend([probability[idx], probability[idx], None, None])

    # для пунктирных линий (вертикальные переходы)
    chart_dot_line_x = []
    chart_dot_line_y = []
    for idx, g in enumerate(damage):
        if idx == len(damage) - 1:
            # Последняя вертикаль вниз
            chart_dot_line_x.extend([g, g])
            chart_dot_line_y.extend([probability[idx], probability[idx]])
            chart_dot_line_x.extend([g, g])
            chart_dot_line_y.extend([probability[idx], 0])
            break
        chart_dot_line_x.extend([g, g])
        chart_dot_line_y.extend([probability[idx], probability[idx + 1]])

    # Отрисовка графика
    fig = plt.figure()
    plt.semilogy(chart_line_x, chart_line_y, color='r', linestyle='-', marker='.')
    plt.semilogy(chart_dot_line_x, chart_dot_line_y, color='r', linestyle='--', marker='.')
    plt.title('F/G - диаграмма')
    plt.xlabel('Ущерб, млн.руб')
    plt.ylabel('Вероятность, 1/год')
    plt.grid(True)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------
# Пример использования
# ---------------------------

if __name__ == '__main__':
    # Тестовые данные для F/N
    fn_rows = [
        {"fatalities_count": 1, "scenario_frequency": 1e-4},
        {"fatalities_count": 2, "scenario_frequency": 5e-5},
        {"fatalities_count": 1, "scenario_frequency": 3e-5},
        {"fatalities_count": 3, "scenario_frequency": 1e-5},
        {"fatalities_count": 4, "scenario_frequency": 5e-6},
    ]

    # Тестовые данные для F/G (total_damage в тыс.руб)
    fg_rows = [
        {"total_damage": 1000, "scenario_frequency": 1e-4},  # 1 млн руб
        {"total_damage": 2500, "scenario_frequency": 5e-5},  # 2.5 млн руб
        {"total_damage": 500, "scenario_frequency": 3e-5},  # 0.5 млн руб
        {"total_damage": 5000, "scenario_frequency": 1e-5},  # 5 млн руб
        {"total_damage": 10000, "scenario_frequency": 5e-6},  # 10 млн руб
    ]

    # Используем оригинальный интерфейс: build -> save
    fn_points = build_fn_points(fn_rows)
    save_fn_chart(fn_points, Path("fn_chart.png"))

    fg_points = build_fg_points(fg_rows)
    save_fg_chart(fg_points, Path("fg_chart.png"))

    print("Диаграммы сохранены: fn_chart.png, fg_chart.png")


# ---------------------------
# Pareto (сценарии по риску)
# ---------------------------

def build_pareto_series(rows, value_key):
    """
    rows: list of dicts
    value_key: ключ значения (например 'collective_risk_fatalities' или 'total_damage')
    label формируется как '<equipment_name> / С<scenario_no>'
    """
    series = []

    for r in rows:
        val = r.get(value_key)
        if val is None:
            continue

        label = f"{r.get('equipment_name', '')} / С{r.get('scenario_no')}"
        series.append((label, float(val)))

    # сортировка по убыванию вклада
    series.sort(key=lambda x: x[1], reverse=True)
    return series

def save_pareto_chart(series, path: Path, title: str, ylabel: str):
    if not series:
        return

    # --- ограничиваем Top-20 ---
    series = limit_pareto_series(series, top_n=20)

    labels = [s[0] for s in series]
    values = [s[1] for s in series]

    total = sum(values)
    cum_values = []
    s = 0.0
    for v in values:
        s += v
        cum_values.append(100.0 * s / total if total > 0 else 0.0)

    x = range(len(values))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x, values)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)

    ax2 = ax.twinx()
    ax2.plot(
        x,
        cum_values,
        color="orange",
        marker="o",
        linewidth=2,
    )
    ax2.set_ylabel("Накопленная доля, %")
    ax2.set_ylim(0, 105)

    # линия 80% по правой оси
    ax2.axhline(
        y=80,
        color="red",
        linestyle="--",
        linewidth=1.5,
    )

    ax.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()

def limit_pareto_series(series, top_n=20):
    """
    series: list of (label, value), отсортированный по убыванию value
    Возвращает Top-N + ('Прочие', сумма остальных)
    """
    if not series or len(series) <= top_n:
        return series

    head = series[:top_n]
    tail = series[top_n:]
    other_sum = sum(v for _, v in tail)

    if other_sum > 0:
        head.append(("Прочие", other_sum))
    return head


def save_component_damage_chart(rows, path: Path, title: str = "Распределение ущерба по составляющим ОПО"):
    """
    rows: list of dicts with keys:
      - hazard_component
      - max_direct_losses
      - max_total_environmental_damage
    """
    if not rows:
        return

    # подготовка + сортировка по сумме
    data = []
    for r in rows:
        comp = r.get("hazard_component")
        d = r.get("max_direct_losses")
        e = r.get("max_total_environmental_damage")
        if comp is None:
            continue
        d = float(d) if d is not None else 0.0
        e = float(e) if e is not None else 0.0
        data.append((str(comp), d, e))

    if not data:
        return

    data.sort(key=lambda x: (x[1] + x[2]), reverse=True)

    labels = [x[0] for x in data]
    direct = [x[1] for x in data]
    env = [x[2] for x in data]

    x = list(range(len(labels)))

    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    # stacked bar: нижний сегмент Прямой, сверху Экологический
    ax.bar(x, direct, label="Прямой")
    ax.bar(x, env, bottom=direct, label="Экологический")

    ax.set_title(title)
    ax.set_xlabel("Составляющая ОПО")
    ax.set_ylabel("Ущерб, тыс. руб")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", labelrotation=90, labelsize=8)

    ax.grid(True, axis="y")
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
