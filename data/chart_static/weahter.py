from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # стабильный backend (без GUI/ошибок в PyCharm)
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def build_monthly_weather_chart(excel_path: Path, out_png: Path, sheet_name: str = "Лист1") -> None:
    # --- Read ---
    df0 = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")

    # В вашем файле первая строка после заголовков содержит "единицы/подписи" -> удаляем
    df = df0.iloc[1:].copy()

    # Берём строго нужные колонки
    df = df[["Дата", "Средняя", "Скорость", "Осадки, мм"]].copy()

    # --- Types (ключевое: dayfirst=True, иначе месяцы съезжают) ---
    df["Дата"] = pd.to_datetime(df["Дата"].astype(str), dayfirst=True, errors="coerce")
    df["Средняя"] = pd.to_numeric(df["Средняя"], errors="coerce")
    df["Скорость"] = pd.to_numeric(df["Скорость"], errors="coerce")
    df["Осадки, мм"] = pd.to_numeric(df["Осадки, мм"], errors="coerce")
    df = df.dropna(subset=["Дата"])

    # --- Monthly aggregation (all years in file) ---
    df["month"] = df["Дата"].dt.month
    monthly = (df.groupby("month", as_index=False)
                 .agg(
                     temp_mean=("Средняя", "mean"),
                     wind_mean=("Скорость", "mean"),
                     precip_sum=("Осадки, мм", "sum"),
                 ))

    monthly = monthly.set_index("month").reindex(range(1, 13)).reset_index()

    # --- Arrays ---
    ru_months = ["янв.","февр.","март","апр.","май","июнь","июль","авг.","сент.","окт.","нояб.","дек."]
    x = np.arange(12)

    temp = monthly["temp_mean"].to_numpy()
    wind = monthly["wind_mean"].to_numpy()
    prec = monthly["precip_sum"].to_numpy()

    # --- Style ---
    plt.rcParams.update({
        "savefig.dpi": 300,
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.labelsize": 12,
        "axes.titleweight": "semibold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig = plt.figure(figsize=(12, 7.5), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1])

    ax_top = fig.add_subplot(gs[0, 0])
    ax_bot = fig.add_subplot(gs[1, 0], sharex=ax_top)

    # --- Top: Temperature (left) ---
    ax_top.plot(x, temp, marker="o", linewidth=2.4, color="#1f77b4", label="Средняя температура")
    ax_top.set_ylabel("Температура, °C")
    ax_top.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax_top.yaxis.set_major_locator(MaxNLocator(nbins=7))

    # --- Top: Wind (right) ---
    ax_wind = ax_top.twinx()
    ax_wind.plot(x, wind, marker="s", linewidth=2.4, color="#2ca02c", label="Скорость ветра")
    ax_wind.set_ylabel("Скорость ветра, м/с")
    ax_wind.set_ylim(bottom=0)
    ax_wind.yaxis.set_major_locator(MaxNLocator(nbins=6))

    # --- Legend centered at bottom of top plot ---
    lines = ax_top.get_lines() + ax_wind.get_lines()
    labels = [l.get_label() for l in lines]
    ax_top.legend(
        lines, labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.18),
        frameon=False,
        ncol=2
    )

    # --- Bottom: Precipitation bars ---
    bars = ax_bot.bar(x, prec, width=0.7, edgecolor="black", linewidth=0.6, alpha=0.9)
    ax_bot.set_ylabel("Осадки, мм/мес")
    ax_bot.set_xlabel("Месяцы")
    ax_bot.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax_bot.yaxis.set_major_locator(MaxNLocator(nbins=6))

    ax_bot.set_xticks(x)
    ax_bot.set_xticklabels(ru_months)

    # Optional: labels on bars (comment out if not needed)
    pmax = np.nanmax(prec) if np.isfinite(np.nanmax(prec)) else 0
    for rect, v in zip(bars, prec):
        if np.isfinite(v) and v > 0:
            ax_bot.text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_height() + pmax * 0.015,
                f"{v:.0f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

    ax_top.set_title("Средняя температура, скорость ветра и осадки по месяцам")

    # --- Save PNG only ---
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    excel_path = BASE_DIR / "Данные.xlsx"
    out_png = BASE_DIR / "monthly_weather.png"

    build_monthly_weather_chart(excel_path, out_png)
    print("Saved:", out_png)
