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
from matplotlib.ticker import MultipleLocator, MaxNLocator

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
    if not points:
        return

    plot_points = [(x, y) for x, y in points if x > 0]
    if len(plot_points) < 1:
        return

    people = [int(p[0]) for p in plot_points]
    probability = [p[1] for p in plot_points]

    chart_line_x = []
    chart_line_y = []
    for idx, n in enumerate(people):
        chart_line_x.extend([n - 1, n, n, n])
        chart_line_y.extend([probability[idx], probability[idx], None, None])

    chart_dot_line_x = []
    chart_dot_line_y = []
    for idx, n in enumerate(people):
        if idx == len(people) - 1:
            chart_dot_line_x.extend([n, n])
            chart_dot_line_y.extend([probability[idx], 0])
            break
        chart_dot_line_x.extend([n, n])
        chart_dot_line_y.extend([probability[idx], probability[idx + 1]])

    # --- Отрисовка графика ---
    fig, ax = plt.subplots()

    ax.semilogy(chart_line_x, chart_line_y, color='b', linestyle='-', marker='.')
    ax.semilogy(chart_dot_line_x, chart_dot_line_y, color='b', linestyle='--', marker='.')

    ax.set_title('F/N - диаграмма')
    ax.set_xlabel('Количество погибших, чел')
    ax.set_ylabel('Вероятность, 1/год')
    ax.grid(True)

    # ✅ 1) Гарантируем только целые значения по оси X
    ax.xaxis.set_major_locator(MultipleLocator(1))          # шаг 1
    ax.xaxis.set_minor_locator(MaxNLocator(integer=True))   # на всякий случай
    ax.set_xticks(sorted(set(people)))                      # подписи только на N из данных

    # ✅ 2) Ограничим X так, чтобы не появлялись дробные границы
    xmin = max(0, min(people) - 1)
    xmax = max(people)
    ax.set_xlim(xmin, xmax)

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

    # series уже отсортирован по убыванию (build_pareto_series)
    series_full = list(series)  # ВСЕ сценарии (для корректного total)

    # --- ограничиваем Top-20 + ("Прочие", сумма хвоста) ---
    series_top = limit_pareto_series(series_full, top_n=20)

    # --- "Прочие" НЕ рисуем столбцом, но учитываем в total ---
    other_value = 0.0
    if series_top and str(series_top[-1][0]).strip().lower() in ("прочие", "прочее"):
        other_value = float(series_top[-1][1])
        series_draw = series_top[:-1]
    else:
        series_draw = series_top

    labels = [s[0] for s in series_draw]
    values = [float(s[1]) for s in series_draw]

    # total должен быть по всем сценариям, включая "прочие"
    total = sum(float(v) for _, v in series_full)

    # накопленная доля считаем по показанным столбцам, но делим на общий total
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

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.tick_params(axis="x", labelrotation=90, labelsize=7)

    ax2 = ax.twinx()
    ax2.plot(
        list(x),
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


def save_component_damage_chart(rows: list[dict], path: Path):
    import textwrap
    """
    Понятный график ущерба по составляющим ОПО:

    - Горизонтальные столбцы (barh)
    - Логарифмическая шкала по оси X (ущерб)
    - Два ряда: Прямой и Экологический (НЕ stack)
    - Сортировка по сумме (Прямой+Экологический) по убыванию
    """
    if not rows:
        return

    def pick(d: dict, keys: list[str], default=0.0) -> float:
        for k in keys:
            if k in d and d.get(k) is not None:
                try:
                    return float(d.get(k))
                except Exception:
                    return default
        return default

    # Под разные схемы именования в твоих данных
    direct_keys = ["max_direct_losses", "direct_losses", "max_total_damage", "total_damage"]
    env_keys = ["max_environmental_losses", "environmental_losses",
                "max_total_environmental_damage", "total_environmental_damage"]

    data = []
    for r in rows:
        comp = r.get("hazard_component")
        if not comp:
            continue
        direct = pick(r, direct_keys, 0.0)
        env = pick(r, env_keys, 0.0)
        total = max(0.0, direct) + max(0.0, env)
        # если вообще ноль — можно не показывать
        if total <= 0:
            continue
        data.append((str(comp), max(0.0, direct), max(0.0, env), total))

    if not data:
        return

    # сортировка: самые большие сверху
    data.sort(key=lambda x: x[3], reverse=True)

    labels = [textwrap.fill(x[0], width=28) for x in data]
    direct_vals = [x[1] for x in data]
    env_vals = [x[2] for x in data]

    # логарифм не принимает 0: поднимем нули до eps только для отрисовки
    eps = 1e-6
    direct_plot = [v if v > 0 else eps for v in direct_vals]
    env_plot = [v if v > 0 else eps for v in env_vals]

    n = len(labels)
    # высота фигуры масштабируется от числа строк
    fig_h = max(4.5, 0.55 * n)
    plt.figure(figsize=(14, fig_h))

    # Две полосы на категорию (рядом)
    y = list(range(n))
    h = 0.35
    y_direct = [yy - h/2 for yy in y]
    y_env = [yy + h/2 for yy in y]

    plt.barh(y_direct, direct_plot, height=h, label="Прямой")
    plt.barh(y_env, env_plot, height=h, label="Экологический")

    ax = plt.gca()
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)

    ax.set_xlabel("Ущерб, тыс. руб. (логарифмическая шкала)")
    ax.set_ylabel("Составляющая ОПО")
    ax.set_title("Распределение ущерба по составляющим ОПО")

    ax.grid(True, axis="x", which="both")
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def save_risk_matrix_chart(rows, path: Path, title: str = "Матрица риска (частота – последствия)"):
    """
    Специализированная матрица:
      X = fatalities_count (строго целое, без jitter)
      Y = scenario_frequency (лог)
      Размер точки ~ частоте
      Подписи: 5 наиболее вероятных + 5 наиболее опасных
      Подписи чередуются фиксированными смещениями (без collision-логики)
    """
    if not rows:
        return

    pts = []
    for r in rows:
        try:
            x = int(r.get("fatalities_count"))
            y = float(r.get("scenario_frequency"))
        except Exception:
            continue
        if x < 1 or y <= 0:
            continue
        pts.append((x, y, r.get("scenario_no")))

    if not pts:
        return

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    import math
    y_min, y_max = min(ys), max(ys)
    denom = (math.log10(y_max) - math.log10(y_min)) if y_max > y_min else 1.0

    sizes = []
    for y in ys:
        t = (math.log10(y) - math.log10(y_min)) / (denom + 1e-12)
        t = max(0.0, min(1.0, t))
        sizes.append(25 + 60 * t)

    # линии матрицы (дефолтные пороги)
    freq_levels = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
    cons_levels = [1, 3, 10]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_yscale("log")

    # горизонтальные линии по частоте
    for f in freq_levels:
        if abs(f - 1e-6) < 1e-12:
            ax.axhline(f, color="green", linestyle="--", linewidth=1.5)
        elif abs(f - 1e-4) < 1e-12:
            ax.axhline(f, color="red", linestyle="--", linewidth=1.5)
        else:
            ax.axhline(f, linewidth=1)

    # вертикальные линии по последствиям
    for n in cons_levels:
        ax.axvline(n, linewidth=1)

    # ✅ точки строго на целых X (без jitter)
    ax.scatter(xs, ys, s=sizes)

    # -----------------------------
    # Подписи: 5 наиболее вероятных + 5 наиболее опасных
    # -----------------------------
    # наиболее вероятные: max frequency
    top_prob = sorted(pts, key=lambda t: t[1], reverse=True)[:5]

    # наиболее опасные: max fatalities, при равенстве — max frequency
    top_dang = sorted(pts, key=lambda t: (t[0], t[1]), reverse=True)[:5]

    label_ids = set()
    for _, _, sc_no in top_prob + top_dang:
        if sc_no is not None:
            label_ids.add(sc_no)

    # фиксированные смещения (чередуются)
    offsets = [
        (4, 3),
        (4, -10),
        (12, 6),
        (12, -14),
    ]

    k = 0
    for x, y, sc_no in pts:
        if sc_no is None or sc_no not in label_ids:
            continue

        dx, dy = offsets[k % len(offsets)]
        k += 1

        ax.annotate(
            f"С{sc_no}",
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=11,
        )

    ax.set_title(title)
    ax.set_xlabel("Последствия: число погибших, чел")
    ax.set_ylabel("Частота сценария, 1/год")

    ax.set_xlim(left=0, right=max(xs) + 1)
    ax.set_ylim(bottom=min(ys) / 2, top=max(ys) * 2)

    # только целые по оси X
    ax.xaxis.set_major_locator(MultipleLocator(1))

    ax.grid(True, which="both")

    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)




def save_risk_matrix_chart_damage(rows, path: Path, title: str = "Матрица риска (частота – ущерб)"):
    """
    X = total_damage (млн руб), без jitter
    Y = scenario_frequency (1/год), лог шкала
    Размер точки ~ частоте
    Подписи: 5 наиболее вероятных + 5 наиболее опасных
    Подписи чередуются с отступами (без collision-логики)
    """
    if not rows:
        return

    pts = []
    for r in rows:
        try:
            x = float(r.get("total_damage")) / 1000.0  # тыс.руб -> млн.руб
            y = float(r.get("scenario_frequency"))
        except Exception:
            continue
        if x <= 0 or y <= 0:
            continue
        pts.append((x, y, r.get("scenario_no")))

    if not pts:
        return

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    import math
    y_min, y_max = min(ys), max(ys)
    denom = (math.log10(y_max) - math.log10(y_min)) if y_max > y_min else 1.0

    sizes = []
    for y in ys:
        t = (math.log10(y) - math.log10(y_min)) / (denom + 1e-12)
        t = max(0.0, min(1.0, t))
        sizes.append(25 + 60 * t)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_yscale("log")

    # точки строго на своих X
    ax.scatter(xs, ys, s=sizes)

    # -----------------------------
    # Подписи: 5 наиболее вероятных + 5 наиболее опасных
    # -----------------------------
    top_prob = sorted(pts, key=lambda t: t[1], reverse=True)[:5]
    top_dang = sorted(pts, key=lambda t: (t[0], t[1]), reverse=True)[:5]

    label_ids = set()
    for _, _, sc_no in top_prob + top_dang:
        if sc_no is not None:
            label_ids.add(sc_no)

    # фиксированные смещения (чередуются)
    offsets = [
        (4, 3),
        (4, -10),
        (12, 6),
        (12, -14),
    ]

    k = 0
    for x, y, sc_no in pts:
        if sc_no is None or sc_no not in label_ids:
            continue

        dx, dy = offsets[k % len(offsets)]
        k += 1

        ax.annotate(
            f"С{sc_no}",
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=11,
        )

    ax.set_title(title)
    ax.set_xlabel("Последствия: суммарный ущерб, млн руб")
    ax.set_ylabel("Частота сценария, 1/год")

    ax.set_xlim(left=0, right=max(xs) * 1.05)
    ax.set_ylim(bottom=min(ys) / 2, top=max(ys) * 2)

    ax.grid(True, which="both")

    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


