import json
from pathlib import Path

from docx import Document

from report.paths import BASE_DIR, DB_PATH, TEMPLATE_PATH, OUT_PATH
from report.db import (
    open_db,
    get_used_substances,
    get_used_equipment,
    get_hazard_distribution,
    get_scenarios,
    get_ov_amounts_in_accident,
)
from report.sections import SUBSTANCE_SECTIONS, EQUIPMENT_SECTIONS
from report.formatters import (
    format_value,
    pretty_json_substance,
    pretty_json_generic,
    format_exp,
    format_float_3,
)
from report.word_utils import (
    find_paragraph_with_marker,
    clear_paragraph,
    insert_paragraph_after,
    insert_table_after,
    insert_paragraph_after_table,
    add_section_header_row,
    set_run_font,
)


def set_cell_text(cell, text, bold: bool = False):
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


def render_distribution_table_at_marker(doc: Document, marker: str, title: str, rows: list[dict]):
    """
    Горизонтальная таблица:
    1) Наименование оборудования
    2) Наименование вещества
    3) Количество опасного вещества, т
    4) Агрегатное состояние
    5) Давление, МПа
    6) Температура, °C

    Требование: округление чисел до 3 знаков после запятой.
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
        set_cell_text(row[2], format_float_3(r.get("amount_t")))
        set_cell_text(row[3], r.get("phase_state") if r.get("phase_state") is not None else "-")
        set_cell_text(row[4], format_float_3(r.get("pressure_mpa")))
        set_cell_text(row[5], format_float_3(r.get("substance_temperature_c")))

    insert_paragraph_after_table(doc, table, "")


def render_ov_amount_table_at_marker(doc: Document, marker: str, title: str, rows: list[dict]):
    """
    Таблица: Оценка количества опасного вещества в аварии
    Колонки:
      1) № п/п
      2) Наименование оборудования
      3) Номер сценария (С{scenario_no})
      4) Количество ОВ участвующего в аварии, т (ov_in_accident_t)
      5) Количество ОВ в создании поражающего фактора, т (ov_in_hazard_factor_t)

    Требование: округление чисел до 3 знаков после запятой.
    """
    p_marker = find_paragraph_with_marker(doc, marker)
    if p_marker is None:
        return

    clear_paragraph(p_marker)

    p = insert_paragraph_after(doc, p_marker, title)
    if p.runs:
        set_run_font(p.runs[0], bold=True)

    table = insert_table_after(doc, p, rows=1, cols=5, style="Table Grid")

    hdr = table.rows[0].cells
    set_cell_text(hdr[0], "№ п/п", bold=True)
    set_cell_text(hdr[1], "Наименование оборудования", bold=True)
    set_cell_text(hdr[2], "Номер сценария", bold=True)
    set_cell_text(hdr[3], "Количество ОВ участвующего в аварии, т", bold=True)
    set_cell_text(hdr[4], "Количество ОВ в создании поражающего фактора, т", bold=True)


    # Порядок С1..Сn, внутри номера — по оборудованию
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            int(r.get("scenario_no")) if r.get("scenario_no") is not None else 10**9,
            str(r.get("equipment_name") or ""),
        ),
    )

    for idx, r in enumerate(rows_sorted, start=1):
        row = table.add_row().cells
        set_cell_text(row[0], idx)
        set_cell_text(row[1], r.get("equipment_name") or "-")
        sc_no = r.get("scenario_no")
        set_cell_text(row[2], f"С{sc_no}" if sc_no is not None else "-")
        set_cell_text(row[3], format_float_3(r.get("ov_in_accident_t")))
        set_cell_text(row[4], format_float_3(r.get("ov_in_hazard_factor_t")))

    insert_paragraph_after_table(doc, table, "")


def _load_typical_scenarios() -> dict:
    """typical_scenarios.json не изменяем; читаем из стандартных мест."""
    candidates = [
        BASE_DIR / "calc" / "typical_scenarios.json",
        BASE_DIR / "typical_scenarios.json",
    ]
    for p in candidates:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _scenario_item_to_text(item) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        # поддержка {"scenario_text": "..."} и близких вариантов
        return str(item.get("scenario_text") or item.get("text") or item.get("description") or "Описание не задано")
    return "Описание не задано"


def _get_scenarios_root(typical: dict) -> dict:
    # root может быть либо сразу словарём, либо лежать в ключе "scenarios"
    if isinstance(typical, dict) and "scenarios" in typical and isinstance(typical["scenarios"], dict):
        return typical["scenarios"]
    return typical if isinstance(typical, dict) else {}


def _get_description_list(root: dict, equipment_type, kind):
    # основной формат: root[equipment_type][kind] -> list
    et = str(equipment_type)
    kd = str(kind)
    if et in root and isinstance(root[et], dict) and kd in root[et]:
        return root[et][kd]
    # запасной вариант: root[kind][equipment_type]
    if kd in root and isinstance(root[kd], dict) and et in root[kd]:
        return root[kd][et]
    return None


def _build_scenario_index(rows: list[dict]):
    """
    Для каждой пары (equipment_type, kind) строим отображение:
    scenario_no (уникальный, отсортированный) -> локальный индекс 0..N-1
    """
    mapping = {}
    for r in rows:
        key = (r.get("equipment_type"), r.get("substance_kind"))
        mapping.setdefault(key, set()).add(r.get("scenario_no"))

    idx_map = {}
    for key, sc_set in mapping.items():
        sc_list = sorted([x for x in sc_set if x is not None])
        idx_map[key] = {sc_no: i for i, sc_no in enumerate(sc_list)}
    return idx_map


def render_scenarios_table_at_marker(doc: Document, marker: str, title: str, rows: list[dict]):
    """
    Таблица сценариев:
    1) № п/п
    2) Наименование оборудования
    3) Номер сценария (С{scenario_no})
    4) Описание сценария (typical_scenarios.json по (equipment_type, kind) и позиции)
    5) Базовая частота, 1/год (base_frequency, экспонента)
    6) Условная вероятность, -
    7) Частота сценария аварии, 1/год (scenario_frequency, экспонента)
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

    typical = _load_typical_scenarios()
    root = _get_scenarios_root(typical)
    idx_map = _build_scenario_index(rows)

    # Порядок: С1..Сn, внутри — по оборудованию
    rows_sorted = sorted(
        rows,
        key=lambda r: (
            int(r.get("scenario_no")) if r.get("scenario_no") is not None else 10**9,
            str(r.get("equipment_name") or ""),
        ),
    )

    for i, r in enumerate(rows_sorted, start=1):
        et = r.get("equipment_type")
        kd = r.get("substance_kind")
        sc_no = r.get("scenario_no")

        local_idx = idx_map.get((et, kd), {}).get(sc_no, None)
        desc_list = _get_description_list(root, et, kd)
        if isinstance(desc_list, list) and local_idx is not None and 0 <= local_idx < len(desc_list):
            desc = _scenario_item_to_text(desc_list[local_idx])
        else:
            desc = "Описание не задано"

        row = table.add_row().cells
        set_cell_text(row[0], i)
        set_cell_text(row[1], r.get("equipment_name") or "-")
        set_cell_text(row[2], f"С{sc_no}" if sc_no is not None else "-")
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
        ov_amounts = get_ov_amounts_in_accident(conn)

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

    render_ov_amount_table_at_marker(
        doc=doc,
        marker="{{OV_AMOUNT_SECTION}}",
        title="Оценка количества опасного вещества в аварии",
        rows=ov_amounts,
    )

    doc.save(OUT_PATH)
    print("Отчёт сформирован:", OUT_PATH)


if __name__ == "__main__":
    main()
