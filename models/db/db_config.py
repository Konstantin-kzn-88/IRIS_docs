# models/db/db_config.py
import os

# models/db/iris.db
MODELS_DIR = os.path.dirname(os.path.dirname(__file__))  # .../models
DB_PATH = os.path.join(MODELS_DIR, "db", "iris.db")
