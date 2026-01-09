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


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open_db(DB_PATH) as conn:
        substances = get_used_substances(conn)
        equipment = get_used_equipment(conn)
        distribution = get_hazard_distribution(conn)

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

    doc.save(OUT_PATH)
    print("Отчёт сформирован:", OUT_PATH)


if __name__ == "__main__":
    main()
