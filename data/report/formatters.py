import json

# ключ -> (русский, единицы)
FIELD_UNITS = {
    # Физические свойства
    "molar_mass_kg_per_mol": ("Молярная масса", "кг/моль"),
    "density_liquid_kg_per_m3": ("Плотность (жидкость)", "кг/м³"),
    "density_gas_kg_per_m3": ("Плотность (газ)", "кг/м³"),
    "evaporation_heat_J_per_kg": ("Теплота испарения", "Дж/кг"),
    "boiling_point_C": ("Температура кипения", "°C"),

    # Взрыво- и пожароопасность
    "explosion_hazard_class": ("Класс взрывоопасности", ""),
    "flash_point_C": ("Температура вспышки", "°C"),
    "lel_percent": ("НКПР", "%"),
    "autoignition_temp_C": ("Температура самовоспламенения", "°C"),
    "burning_rate_kg_per_s_m2": ("Скорость горения", "кг/(с·м²)"),
    "heat_of_combustion_kJ_per_kg": ("Теплота сгорания", "кДж/кг"),
    "energy_reserve_factor": ("Коэффициент энергетического запаса", ""),
    "expansion_degree": ("Степень расширения", ""),

    # Токсичность
    "hazard_class": ("Класс опасности (токсичность)", ""),
    "pdk_mg_per_m3": ("ПДК", "мг/м³"),
    "threshold_tox_dose_mg_min_per_L": ("Пороговая токсодоза", "мг·мин/л"),
    "lethal_tox_dose_mg_min_per_L": ("Смертельная токсодоза", "мг·мин/л"),
}


def _safe_json_loads(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def format_value(key: str, value) -> str:
    """None -> '-', число + единицы (если известны)."""
    if value is None:
        return "-"

    _, unit = FIELD_UNITS.get(key, (key, ""))

    if isinstance(value, (int, float)):
        return f"{value} {unit}".strip()

    return str(value)


def pretty_json_generic(json_text: str) -> str:
    """Простой красивый JSON (для equipment координат и т.п.)."""
    if not json_text:
        return "-"

    data = _safe_json_loads(json_text)
    if isinstance(data, (dict, list)):
        return json.dumps(data, ensure_ascii=False, indent=2)

    return str(json_text)


def pretty_json_substance(json_text: str) -> str:
    """
    Красивый JSON для веществ: composition notes/components + перевод ключей + размерности + None -> '-'
    """
    if not json_text:
        return "-"

    data = _safe_json_loads(json_text)
    if not isinstance(data, dict):
        return str(json_text)

    lines = []

    # composition-like: notes + components
    if "components" in data or "notes" in data:
        notes = data.get("notes")
        if isinstance(notes, str) and notes.strip():
            lines.append(f"Примечания: {notes.strip()}")

        comps = data.get("components")
        if isinstance(comps, list):
            comp_lines = []
            for c in comps:
                if not isinstance(c, dict):
                    continue
                name = str(c.get("name", "")).strip()
                mf = c.get("mass_fraction")
                if mf is None:
                    if name:
                        comp_lines.append(f"- {name}")
                else:
                    try:
                        comp_lines.append(f"- {name}: {float(mf) * 100:.1f}%")
                    except Exception:
                        comp_lines.append(f"- {name}: {mf}")
            if comp_lines:
                lines.append("Компоненты:\n" + "\n".join(comp_lines))

    # остальные ключи
    for k, v in data.items():
        if k in ("components", "notes"):
            continue
        title, _ = FIELD_UNITS.get(k, (k, ""))
        val = format_value(k, v)
        if val == "None":
            val = "-"
        lines.append(f"{title}: {val}")

    return "\n".join(lines) if lines else "-"


def format_exp(value) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.2e}"
    except Exception:
        return str(value)


def format_float_3(value):
    """
    Округление до 3 знаков после запятой.
    None -> '-'
    """
    if value is None:
        return "-"

    try:
        return f"{float(value):.3f}"
    except Exception:
        return str(value)

def format_float_1(value):
    """
    Округление до 1 знака после запятой.
    None -> '-'
    """
    if value is None:
        return "-"
    try:
        return f"{float(value):.1f}"
    except Exception:
        return str(value)
