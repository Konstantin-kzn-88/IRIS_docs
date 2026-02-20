from __future__ import annotations

CREATE_DB = True # нужно ли создавать базу данных
CREATE_CALC = True # нужно ли проводить расчеты по новой
CREATE_BACKUP = True  # нужно ли создавать архив исходных данных

def main() -> None:

    if CREATE_DB:
        # 1) Создание/пересоздание БД
        from db.create_sqlite_db import main as create_db
        create_db()

    if CREATE_CALC:
        # 2) Расчёт и запись результатов в БД
        from calculations.create_calc import main as run_calc
        run_calc()

    if CREATE_BACKUP:
        from report.backup import create_backup
        create_backup()

    # 3) Формирование отчёта (docx +  диаграммы)
    from report.fill_word import main as build_report
    build_report()


if __name__ == "__main__":
    main()
