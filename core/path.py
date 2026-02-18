from pathlib import Path

# IRIS_docs/core/paths.py
CORE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CORE_DIR.parent  # <-- ВАЖНО

# --- DATA ---
DATA_DIR = PROJECT_DIR / "data"

SUBSTANCES_JSON = DATA_DIR / "substances/substances.json"
EQUIPMENT_JSON = DATA_DIR / "equipments/equipments.json"
TYPICAL_SCENARIOS_PATH = DATA_DIR / "typical_scenarios.json"

# --- DATABASE ---
DB_DIR = PROJECT_DIR / "db"
DB_PATH = DB_DIR / "iris.sqlite3"
SCHEMA_PATH = DB_DIR / "schema.sql"

# --- REPORT ---
# Какой шаблон использовать
# VARIANT_TEMPLATE = "Tatneft/ДПБ_(экспл_стац)"
VARIANT_TEMPLATE = 'default'
# для какой организации
VARIANT_ORG = "tatneft"
# какого ОПО
ORGANIZATION_SITE_ID = "opo_1448"
# ------

# --- INFO ---
INFO_DIR = PROJECT_DIR / "info"

ORGANIZATION_PATH = Path(f"data/organizations/{VARIANT_ORG}/organization.json")
PROJECT_COMMON_PATH = PROJECT_DIR / "data" / "project_common.json"


# --- REPORT ---
REPORT_DIR = PROJECT_DIR / "report"

REPORT_TEMPLATE_DIR = REPORT_DIR / "template" / VARIANT_TEMPLATE

# Все docx-шаблоны в выбранной папке
REPORT_TEMPLATE_FILES = sorted(REPORT_TEMPLATE_DIR.glob("*.docx"))

# Вывод: можно складывать в подпапку, чтобы варианты/ОПО не мешались
REPORT_OUTPUT_DIR = REPORT_DIR / "output"
REPORT_CHARTS_DIR = REPORT_OUTPUT_DIR / "charts"

