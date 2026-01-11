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