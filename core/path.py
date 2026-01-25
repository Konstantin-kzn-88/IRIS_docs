from pathlib import Path

# IRIS_docs/core/paths.py
CORE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CORE_DIR.parent  # <-- ВАЖНО

# --- DATA ---
DATA_DIR = PROJECT_DIR / "data"

SUBSTANCES_JSON = DATA_DIR / "substances.json"
EQUIPMENT_JSON = DATA_DIR / "equipment.json"
TYPICAL_SCENARIOS_PATH = DATA_DIR / "typical_scenarios.json"

# --- DATABASE ---
DB_DIR = PROJECT_DIR / "db"
DB_PATH = DB_DIR / "iris.sqlite3"
SCHEMA_PATH = DB_DIR / "schema.sql"

# --- REPORT ---
REPORT_DIR = PROJECT_DIR / "report"

REPORT_TEMPLATE_DIR = REPORT_DIR / "template"
REPORT_TEMPLATE_DOCX = REPORT_TEMPLATE_DIR / "template_report.docx"

REPORT_OUTPUT_DIR = REPORT_DIR / "output"
REPORT_CHARTS_DIR = REPORT_OUTPUT_DIR / "charts"

# --- INFO ---
INFO_DIR = PROJECT_DIR / "info"

ORGANIZATION_PATH = Path("data/organizations/tatneft/organization.json")
ORGANIZATION_SITE_ID = "opo_0866"
