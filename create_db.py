import sqlite3

def create_database():
    """Создание базы данных и всех необходимых таблиц"""
    conn = sqlite3.connect('industrial_safety.db')
    cursor = conn.cursor()

    # Создание таблицы организаций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        full_name TEXT NOT NULL,
        org_form TEXT NOT NULL,
        head_position TEXT,
        head_name TEXT,
        legal_address TEXT,
        phone TEXT,
        fax TEXT,
        email TEXT,
        license_number TEXT,
        license_date TEXT,
        ind_safety_system TEXT,
        prod_control TEXT,
        accident_investigation TEXT,
        rescue_contract TEXT,
        rescue_certificate TEXT,
        fire_contract TEXT,
        emergency_certificate TEXT,
        material_reserves TEXT,
        financial_reserves TEXT
    )
    ''')

    # Создание таблицы опасных производственных объектов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dangerous_objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        reg_number TEXT NOT NULL,
        hazard_class TEXT NOT NULL,
        location TEXT NOT NULL,
        employee_count INTEGER NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations (id)
    )
    ''')

    # Создание таблицы проектов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opo_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        automation_description TEXT,
        project_code TEXT,
        dpb_code TEXT,
        rpz_code TEXT,
        ifl_code TEXT,
        gochs_code TEXT,
        mpb_code TEXT,
        FOREIGN KEY (opo_id) REFERENCES dangerous_objects (id)
    )
    ''')

    # Создание таблицы веществ
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS substances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_name TEXT NOT NULL,
        class_substance INTEGER NOT NULL,
        sub_type INTEGER NOT NULL,
        density_liquid REAL,
        molecular_weight REAL,
        boiling_temperature_liquid REAL,
        heat_evaporation_liquid REAL,
        adiabatic REAL,
        heat_capacity_liquid REAL,
        heat_of_combustion REAL,
        sigma INTEGER,
        energy_level INTEGER,
        flash_point REAL,
        auto_ignition_temp REAL,
        lower_concentration_limit REAL,
        upper_concentration_limit REAL,
        threshold_toxic_dose REAL,
        lethal_toxic_dose REAL,
        CHECK (class_substance BETWEEN 1 AND 4),
        CHECK (sub_type BETWEEN 0 AND 7),
        CHECK (sigma IN (4, 7)),
        CHECK (energy_level IN (1, 2))
    )
    ''')

    # Создание таблицы оборудования
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        substance_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        equipment_type TEXT NOT NULL,
        component_enterprise TEXT,
        sub_id TEXT,
        coordinate TEXT,
        pressure REAL,
        temperature REAL,
        FOREIGN KEY (project_id) REFERENCES projects (id),
        FOREIGN KEY (substance_id) REFERENCES substances (id)
    )
    ''')

    # Создание таблицы для трубопроводов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pipelines (
        equipment_id INTEGER PRIMARY KEY,
        diameter_category TEXT NOT NULL,
        length_meters REAL NOT NULL,
        diameter_pipeline REAL NOT NULL,
        flow REAL,
        time_out REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы для насосов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pumps (
        equipment_id INTEGER PRIMARY KEY,
        pump_type TEXT NOT NULL,
        volume REAL,
        flow REAL,
        time_out REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы для технологических устройств
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS technological_devices (
        equipment_id INTEGER PRIMARY KEY,
        device_type TEXT NOT NULL,
        volume REAL,
        degree_filling REAL,
        spill_square REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы для стационарных резервуаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tanks (
        equipment_id INTEGER PRIMARY KEY,
        tank_type TEXT NOT NULL,
        volume REAL,
        degree_filling REAL,
        spill_square REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы для автоцистерн
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS truck_tanks (
        equipment_id INTEGER PRIMARY KEY,
        pressure_type TEXT NOT NULL,
        volume REAL,
        degree_filling REAL,
        spill_square REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы для компрессоров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compressors (
        equipment_id INTEGER PRIMARY KEY,
        comp_type TEXT NOT NULL,
        volume REAL,
        flow REAL,
        time_out REAL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    # Создание таблицы сценариев
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        depressurization_type TEXT NOT NULL,
        probability REAL NOT NULL,
        calculation_method TEXT NOT NULL,
        tree_branch INTEGER NOT NULL,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()