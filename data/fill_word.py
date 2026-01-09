from docx import Document

from report.paths import DB_PATH, TEMPLATE_PATH, OUT_PATH
from report.db import open_db, get_used_substances, get_used_equipment, get_hazard_distribution
from report.sections import SUBSTANCE_SECTIONS, EQUIPMENT_SECTIONS
from report.formatters import format_value, pretty_json_substance, pretty_json_generic
from report.word_utils import (
    find_paragraph_with_marker,
    clear_paragraph,
    insert_paragraph_after,
    insert_table_after,
    insert_paragraph_after_table,
    add_section_header_row, set_run_font
)

import json
from report.db import get_scenarios
from report.formatters import format_exp

from pathlib import Path
from report.paths import BASE_DIR
TYPICAL_SCENARIOS_PATH = BASE_DIR / "calc" / "typical_scenarios.json"

with open(TYPICAL_SCENARIOS_PATH, "r", encoding="utf-8") as f:
    TYPICAL_SCENARIOS = json.load(f)

# typical_scenarios.json может быть либо сразу словарём сценариев, либо иметь корневой ключ "scenarios"
TYPICAL_SCENARIOS_ROOT = TYPICAL_SCENARIOS.get("scenarios", TYPICAL_SCENARIOS)

def _scenario_text(item) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("scenario_text", "Описание не задано"))
    return "Описание не задано"

def attach_local_index(rows: list[dict]) -> list[dict]:
    """
    Для каждой пары (equipment_type, kind) сортируем по scenario_no
    и присваиваем локальный индекс 0..N-1.
    """
    groups = {}
    for r in rows:
        key = (r["equipment_type"], r["substance_kind"])
        groups.setdefault(key, []).append(r)

    out = []
    for key, items in groups.items():
        items_sorted = sorted(items, key=lambda x: (x["scenario_no"] if x["scenario_no"] is not None else 0))
        for i, r in enumerate(items_sorted):
            rr = dict(r)
            rr["_local_idx"] = i
            out.append(rr)

    # можно вернуть в удобной сортировке по оборудованию/сценарию
    return sorted(out, key=lambda x: (x["equipment_name"], x["equipment_type"], x["substance_kind"], x["scenario_no"]))


def get_description(equipment_type, kind, local_idx) -> str:
    try:
        lst = TYPICAL_SCENARIOS[str(equipment_type)][str(kind)]
        if not isinstance(lst, list):
            return "Описание не задано"
        if local_idx < 0 or local_idx >= len(lst):
            return "Описание не задано"
        return _scenario_text(lst[local_idx])
    except Exception:
        return "Описание не задано"



def set_cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    set_run_font(run, bold=bold)

def fill_table(table, obj: dict, sections, json_formatter):
    for section_title, fields in sections:
        rows = []
        for field, label in fields:
            raw = obj.get(field)

            if field.endswith("_json"):
                value = json_formatter(raw)
            else:
                value = format_value(field, raw)

            # Не выводим пустое. "-" не выводим (если нужно выводить — убери "-")
            if value is None:
                continue
            if isinstance(value, str) and value.strip() in ("", "-"):
                continue

            rows.append((label, value))

        if not rows:
            continue

        add_section_header_row(table, section_title)
        for label, value in rows:
            r = table.add_row().cells
            set_cell_text(r[0], label)
            set_cell_text(r[1], value)


def render_section_at_marker(
    doc: Document,
    marker: str,
    section_title: str,
    items: list[dict],
    item_title_field: str,
    sections,
    json_formatter,
):
    p_marker = find_paragraph_with_marker(doc, marker)
    if p_marker is None:
        return

    clear_paragraph(p_marker)

    p = insert_paragraph_after(doc, p_marker, section_title)
    if p.runs:
        set_run_font(p.runs[0], bold=True)

    cur = p
    for item in items:
        item_title = item.get(item_title_field, "—")
        cur = insert_paragraph_after(doc, cur, str(item_title))
        if cur.runs:
            set_run_font(cur.runs[0], bold=True)

        table = insert_table_after(doc, cur, rows=0, cols=2, style="Table Grid")
        fill_table(table, item, sections, json_formatter)

        cur = insert_paragraph_after_table(doc, table, "")


def _fmt_number(x, suffix=""):
    if x is None:
        return "-"
    try:
        # аккуратно: без научной нотации, разумно по месту
        v = float(x)
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        return (s + suffix).strip()
    except Exception:
        return str(x)


def render_distribution_table_at_marker(doc: Document, marker: str, title: str, rows: list[dict]):
    """
    Горизонтальная таблица:
    1) Наименование оборудования
    2) Наименование вещества
    3) Количество опасного вещества, т
    4) Агрегатное состояние
    5) Давление, МПа
    6) Температура, °C
    """
    p_marker = find_paragraph_with_marker(doc, marker)
    if p_marker is None:
        return

    clear_paragraph(p_marker)

    p = insert_paragraph_after(doc, p_marker, title)
    if p.runs:
        set_run_font(p.runs[0], bold=True)

    table = insert_table_after(doc, p, rows=1, cols=6, style="Table Grid")
    hdr = table.rows[0].cells
    set_cell_text(hdr[0], "Наименование оборудования", bold=True)
    set_cell_text(hdr[1], "Наименование вещества", bold=True)
    set_cell_text(hdr[2], "Количество опасного вещества, т", bold=True)
    set_cell_text(hdr[3], "Агрегатное состояние", bold=True)
    set_cell_text(hdr[4], "Давление, МПа", bold=True)
    set_cell_text(hdr[5], "Температура, °C", bold=True)

    for r in rows:
        row = table.add_row().cells
        set_cell_text(row[0], r.get("equipment_name") or "-")
        set_cell_text(row[1], r.get("substance_name") or "-")
        set_cell_text(row[2], _fmt_number(r.get("amount_t")))
        set_cell_text(row[3], r.get("phase_state") if r.get("phase_state") is not None else "-")
        set_cell_text(row[4], _fmt_number(r.get("pressure_mpa")))
        set_cell_text(row[5], _fmt_number(r.get("substance_temperature_c")))

    insert_paragraph_after_table(doc, table, "")

# -------------------------------------------------
# Сценарии: описание из typical_scenarios.json
# Формат: scenarios[equipment_type][kind] -> list[ str | {"scenario_text": "..."} ]
# scenario_no в calculations - сквозная нумерация; описание берём по позиции внутри пары (equipment_type, kind)
# -------------------------------------------------
def build_scenario_index_map(rows: list[dict]) -> dict:
    """
    Для каждой пары (equipment_type, kind) строим отображение:
    scenario_no -> локальный индекс (0..N-1), где N = число уникальных scenario_no для этой пары.
    Это корректно при наличии нескольких единиц оборудования с одинаковой парой (equipment_type, kind).
    """
    pair_to_set = {}
    for r in rows:
        et = r.get("equipment_type")
        k = r.get("substance_kind")
        sn = r.get("scenario_no")
        if et is None or k is None or sn is None:
            continue
        pair_to_set.setdefault((et, k), set()).add(sn)

    pair_to_map = {}
    for pair, sset in pair_to_set.items():
        ordered = sorted(sset)
        pair_to_map[pair] = {sn: i for i, sn in enumerate(ordered)}
    return pair_to_map


def get_scenario_description(equipment_type, kind, scenario_no, index_map: dict) -> str:
    """
    В typical_scenarios.json описания заданы списком по паре (equipment_type, kind).
    scenario_no в calculations — сквозной номер; берём позицию в списке по локальному индексу
    внутри пары (equipment_type, kind) согласно отсортированным уникальным scenario_no для этой пары.
    Поддерживаем варианты структуры:
      - root[equipment_type][kind] -> list
      - root[kind][equipment_type] -> list  (на случай иной вложенности)
      - root может быть в ключе "scenarios"
    """
    try:
        local_idx = index_map.get((equipment_type, kind), {}).get(scenario_no, None)
        if local_idx is None:
            return "Описание не задано"

        root = TYPICAL_SCENARIOS_ROOT

        lst = None
        # основной вариант: [equipment_type][kind]
        try:
            lst = root[str(equipment_type)][str(kind)]
        except Exception:
            lst = None

        # запасной вариант: [kind][equipment_type]
        if lst is None:
            try:
                lst = root[str(kind)][str(equipment_type)]
            except Exception:
                lst = None

        if not isinstance(lst, list):
            return "Описание не задано"
        if local_idx < 0 or local_idx >= len(lst):
            return "Описание не задано"

        return _scenario_text(lst[local_idx])
    except Exception:
        return "Описание не задано"


def render_scenarios_table_at_marker(doc: Document, marker: str, title: str, rows: list[dict]):
    """
    Таблица:
    1. № п/п
    2. Наименование оборудования (equipment_name)
    3. Номер сценария (С{scenario_no})
    4. Описание сценария (typical_scenarios.json по equipment_type/kind и позиции)
    5. Базовая частота, 1/год (base_frequency) - экспоненциальная
    6. Условная вероятность, - (accident_event_probability)
    7. Частота сценария аварии, 1/год (scenario_frequency) - экспоненциальная
    """
    p_marker = find_paragraph_with_marker(doc, marker)
    if p_marker is None:
        return

    clear_paragraph(p_marker)

    p = insert_paragraph_after(doc, p_marker, title)
    if p.runs:
        set_run_font(p.runs[0], bold=True)

    table = insert_table_after(doc, p, rows=1, cols=7, style="Table Grid")
    hdr = table.rows[0].cells
    headers = [
        "№ п/п",
        "Наименование оборудования",
        "Номер сценария",
        "Описание сценария",
        "Базовая частота, 1/год",
        "Условная вероятность, -",
        "Частота сценария аварии, 1/год",
    ]
    for i, h in enumerate(headers):
        set_cell_text(hdr[i], h, bold=True)

    # строим индекс соответствия scenario_no -> позиция в списке описаний для пары (equipment_type, kind)
    index_map = build_scenario_index_map(rows)

    # удобная сортировка
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            r.get("scenario_no") if r.get("scenario_no") is not None else 0,
            str(r.get("equipment_name") or ""),
        ),
    )

    for n, r in enumerate(rows_sorted, start=1):
        equipment_name = r.get("equipment_name") or "-"
        scenario_no = r.get("scenario_no")
        equipment_type = r.get("equipment_type")
        substance_kind = r.get("substance_kind")

        desc = get_scenario_description(equipment_type, substance_kind, scenario_no, index_map)

        row = table.add_row().cells
        set_cell_text(row[0], n)
        set_cell_text(row[1], equipment_name)
        set_cell_text(row[2], f"С{scenario_no}" if scenario_no is not None else "-")
        set_cell_text(row[3], desc)
        set_cell_text(row[4], format_exp(r.get("base_frequency")))
        set_cell_text(row[5], r.get("accident_event_probability") if r.get("accident_event_probability") is not None else "-")
        set_cell_text(row[6], format_exp(r.get("scenario_frequency")))

    insert_paragraph_after_table(doc, table, "")


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open_db(DB_PATH) as conn:
        substances = get_used_substances(conn)
        equipment = get_used_equipment(conn)
        distribution = get_hazard_distribution(conn)
        scenarios = get_scenarios(conn)

    doc = Document(TEMPLATE_PATH)

    render_section_at_marker(
        doc=doc,
        marker="{{SUBSTANCES_SECTION}}",
        section_title="Сведения о веществах",
        items=substances,
        item_title_field="name",
        sections=SUBSTANCE_SECTIONS,
        json_formatter=pretty_json_substance,
    )

    render_section_at_marker(
        doc=doc,
        marker="{{EQUIPMENT_SECTION}}",
        section_title="Сведения об оборудовании",
        items=equipment,
        item_title_field="equipment_name",
        sections=EQUIPMENT_SECTIONS,
        json_formatter=pretty_json_generic,
    )

    render_distribution_table_at_marker(
        doc=doc,
        marker="{{DISTRIBUTION_SECTION}}",
        title="Распределение опасного вещества по оборудованию",
        rows=distribution,
    )

    render_scenarios_table_at_marker(
        doc=doc,
        marker="{{SCENARIOS_SECTION}}",
        title="Сценарии аварий",
        rows=scenarios,
    )

    doc.save(OUT_PATH)
    print("Отчёт сформирован:", OUT_PATH)


if __name__ == "__main__":
    main()
