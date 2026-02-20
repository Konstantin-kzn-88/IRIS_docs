from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime


def create_backup() -> None:
    """
    Создает zip-архив исходных данных проекта в report/backup
    и сохраняет структуру каталогов относительно корня проекта.

    В архив включаются:
        - core/path.py
        - data/equipments/equipment_data.xlsx
        - data/equipments/equipments.json
        - data/substances/info.txt
        - data/substances/substances.json
        - data/project_common.json
    """

    # Корень проекта (IRIS_docs)
    project_root = Path(__file__).resolve().parents[1]

    backup_dir = project_root / "report" / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_base = backup_dir / f"source_backup_{timestamp}"
    temp_dir = backup_dir / f"_tmp_{timestamp}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    files_to_copy = [
        project_root / "core" / "path.py",
        project_root / "data" / "equipments" / "equipment_data.xlsx",
        project_root / "data" / "equipments" / "equipments.json",
        project_root / "data" / "substances" / "info.txt",
        project_root / "data" / "substances" / "substances.json",
        project_root / "data" / "project_common.json",
    ]

    try:
        for src in files_to_copy:
            if not src.exists():
                print(f"[WARNING] Файл не найден и не будет добавлен в архив: {src}")
                continue

            # путь внутри архива: относительно корня проекта
            rel = src.relative_to(project_root)
            dst = temp_dir / rel

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        shutil.make_archive(str(archive_base), "zip", temp_dir)
        print(f"[OK] Архив создан: {archive_base}.zip")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)