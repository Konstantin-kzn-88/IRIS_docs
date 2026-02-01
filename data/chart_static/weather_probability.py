from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def build_probability_chart(excel_path: Path, out_png: Path, sheet_name: str = "Лист1") -> None:
    """
    Строит распределения (доли дней):
      - Скорость ветра: 1–<2, 2–<3, 3–<4, 4–≤5, >5
      - Средняя температура: <0, 0–<10, 10–<20, 20–≤30
    """

    # --- Read ---
    df0 = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")

    # Удаляем строку с единицами измерения
    df = df0.iloc[1:].copy()

    df = df[["Дата", "Средняя", "Скорость"]].copy()

    # Корректный парсинг даты
    df["Дата"] = pd.to_datetime(df["Дата"].astype(str), dayfirst=True, errors="coerce")
    df["Средняя"] = pd.to_numeric(df["Средняя"], errors="coerce")
    df["Скорость"] = pd.to_numeric(df["Скорость"], errors="coerce")
    df = df.dropna(subset=["Дата"])

    temp = df["Средняя"].dropna().to_numpy()
    wind = df["Скорость"].dropna().to_numpy()

    # ----------------------------------------------------------------------
    # БИНЫ ДЛЯ ВЕТРА (без <1 м/с)
    # ----------------------------------------------------------------------
    wind_labels = ["1–<2", "2–<3", "3–<4", "4–≤5", ">5"]
    wind_counts = np.array([
        np.sum((wind >= 1) & (wind < 2)),
        np.sum((wind >= 2) & (wind < 3)),
        np.sum((wind >= 3) & (wind < 4)),
        np.sum((wind >= 4) & (wind <= 5)),
        np.sum(wind > 5),
    ], dtype=float)
    wind_probs = wind_counts / wind_counts.sum()

    # ----------------------------------------------------------------------
    # БИНЫ ДЛЯ ТЕМПЕРАТУРЫ (без >=30, объединяем 20–<30)
    # ----------------------------------------------------------------------
    temp_labels = ["<0", "0–<10", "10–<20", "20–≤30,>30"]
    temp_counts = np.array([
        np.sum(temp < 0),
        np.sum((temp >= 0) & (temp < 10)),
        np.sum((temp >= 10) & (temp < 20)),
        np.sum((temp >= 20) & (temp <= 30)),
    ], dtype=float)
    temp_probs = temp_counts / temp_counts.sum()

    # ----------------------------------------------------------------------
    # Plot
    # ----------------------------------------------------------------------
    plt.rcParams.update({
        "savefig.dpi": 300,
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.labelsize": 12,
        "axes.titleweight": "semibold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), constrained_layout=True)

    # --- Wind ---
    xw = np.arange(len(wind_labels))
    bars_w = ax1.bar(
        xw, wind_probs, width=0.75,
        edgecolor="black", linewidth=0.6, alpha=0.9, color="#2ca02c"
    )
    ax1.set_title("Распределение вероятностей: скорость ветра")
    ax1.set_ylabel("Вероятность возникновения")
    ax1.set_xticks(xw)
    ax1.set_xticklabels([f"{l} м/с" for l in wind_labels])
    ax1.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax1.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)

    for r, p in zip(bars_w, wind_probs):
        ax1.text(
            r.get_x() + r.get_width() / 2,
            r.get_height() + 0.01,
            f"{p:.3f}",
            ha="center", va="bottom", fontsize=10
        )

    # --- Temperature ---
    xt = np.arange(len(temp_labels))
    bars_t = ax2.bar(
        xt, temp_probs, width=0.75,
        edgecolor="black", linewidth=0.6, alpha=0.9, color="#1f77b4"
    )
    ax2.set_title("Распределение вероятностей: средняя температура")
    ax2.set_ylabel("Вероятность возникновения")
    ax2.set_xticks(xt)
    ax2.set_xticklabels([f"{l} °C" for l in temp_labels])
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax2.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)

    for r, p in zip(bars_t, temp_probs):
        ax2.text(
            r.get_x() + r.get_width() / 2,
            r.get_height() + 0.01,
            f"{p:.3f}",
            ha="center", va="bottom", fontsize=10
        )

    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    excel_path = BASE_DIR / "Данные.xlsx"
    out_png = BASE_DIR / "probabilities_temp_wind.png"

    build_probability_chart(excel_path, out_png)
    print("Saved:", out_png)
