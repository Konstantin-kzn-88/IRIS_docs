from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # .../data
DB_PATH = BASE_DIR / "iris.sqlite3"
TEMPLATE_PATH = BASE_DIR / "template" / "template_report.docx"
OUT_PATH = BASE_DIR / "fill_template" / "template_report_out.docx"
