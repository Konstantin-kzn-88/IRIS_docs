-- Организации
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
);

-- Опасные производственные объекты
CREATE TABLE IF NOT EXISTS dangerous_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    reg_number TEXT NOT NULL UNIQUE,
    hazard_class TEXT NOT NULL,
    location TEXT NOT NULL,
    employee_count INTEGER NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- Проекты
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opo_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    automation_description TEXT,
    project_code TEXT UNIQUE,
    dpb_code TEXT,
    rpz_code TEXT,
    ifl_code TEXT,
    gochs_code TEXT,
    mpb_code TEXT,
    FOREIGN KEY (opo_id) REFERENCES dangerous_objects(id) ON DELETE CASCADE
);

-- Вещества
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
    lethal_toxic_dose REAL
);

-- Базовое оборудование
CREATE TABLE IF NOT EXISTS base_equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    substance_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    component_enterprise TEXT,
    sub_id TEXT,
    pressure REAL NOT NULL,
    temperature REAL NOT NULL,
    expected_casualties INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (substance_id) REFERENCES substances(id) ON DELETE RESTRICT
);

-- Трубопроводы
CREATE TABLE IF NOT EXISTS pipelines (
    id INTEGER PRIMARY KEY,
    diameter_category TEXT NOT NULL,
    length_meters REAL NOT NULL,
    diameter_pipeline REAL NOT NULL,
    flow REAL,
    time_out REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Насосы
CREATE TABLE IF NOT EXISTS pumps (
    id INTEGER PRIMARY KEY,
    pump_type TEXT NOT NULL,
    volume REAL,
    flow REAL,
    time_out REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Технологические устройства
CREATE TABLE IF NOT EXISTS technological_devices (
    id INTEGER PRIMARY KEY,
    device_type TEXT NOT NULL,
    volume REAL,
    degree_filling REAL,
    spill_square REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Резервуары
CREATE TABLE IF NOT EXISTS tanks (
    id INTEGER PRIMARY KEY,
    tank_type TEXT NOT NULL,
    volume REAL,
    degree_filling REAL,
    spill_square REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Автоцистерны
CREATE TABLE IF NOT EXISTS truck_tanks (
    id INTEGER PRIMARY KEY,
    pressure_type TEXT NOT NULL,
    volume REAL,
    degree_filling REAL,
    spill_square REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Компрессоры
CREATE TABLE IF NOT EXISTS compressors (
    id INTEGER PRIMARY KEY,
    comp_type TEXT NOT NULL,
    volume REAL,
    flow REAL,
    time_out REAL,
    FOREIGN KEY (id) REFERENCES base_equipment(id) ON DELETE CASCADE
);

-- Результаты расчетов
CREATE TABLE IF NOT EXISTS calculation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT NOT NULL,
    scenario_number TEXT NOT NULL,
    equipment_name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    substance_type INTEGER NOT NULL,
    q_10_5 REAL,
    q_7_0 REAL,
    q_4_2 REAL,
    q_1_4 REAL,
    p_53 REAL,
    p_28 REAL,
    p_12 REAL,
    p_5 REAL,
    p_2 REAL,
    l_f REAL,
    d_f REAL,
    r_nkpr REAL,
    r_flash REAL,
    l_pt REAL,
    p_pt REAL,
    q_600 REAL,
    q_320 REAL,
    q_220 REAL,
    q_120 REAL,
    s_spill REAL,
    casualties INTEGER NOT NULL,
    injured INTEGER NOT NULL,
    direct_losses REAL NOT NULL,
    liquidation_costs REAL NOT NULL,
    social_losses REAL NOT NULL,
    indirect_damage REAL NOT NULL,
    environmental_damage REAL NOT NULL,
    total_damage REAL NOT NULL,
    casualty_risk REAL NOT NULL,
    injury_risk REAL NOT NULL,
    expected_damage REAL NOT NULL,
    probability REAL NOT NULL,
    FOREIGN KEY (project_code) REFERENCES projects(project_code) ON DELETE CASCADE
);

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_dangerous_objects_organization ON dangerous_objects(organization_id);
CREATE INDEX IF NOT EXISTS idx_projects_opo ON projects(opo_id);
CREATE INDEX IF NOT EXISTS idx_base_equipment_project ON base_equipment(project_id);
CREATE INDEX IF NOT EXISTS idx_base_equipment_substance ON base_equipment(substance_id);
CREATE INDEX IF NOT EXISTS idx_calculation_results_project ON calculation_results(project_code);