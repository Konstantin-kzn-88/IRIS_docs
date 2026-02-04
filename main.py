from __future__ import annotations

CREATE_DB = False # нужно ли создавать базу данных
CREATE_CALC = False # нужно ли проводить расчеты по новой


def main() -> None:

    if CREATE_DB:
        # 1) Создание/пересоздание БД
        from db.create_sqlite_db import main as create_db
        create_db()

    if CREATE_CALC:
        # 2) Расчёт и запись результатов в БД
        from calculations.create_calc import main as run_calc
        run_calc()

    # 3) Формирование отчёта (docx +  диаграммы)
    from report.fill_word import main as build_report
    build_report()


if __name__ == "__main__":
    main()
