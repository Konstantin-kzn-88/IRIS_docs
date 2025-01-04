-- Организации
INSERT INTO organizations (
    name, full_name, org_form, head_position, head_name,
    legal_address, phone, email, license_number, license_date
) VALUES
-- Первая организация
(
    'АО "НефтеГазПром"',
    'Акционерное общество "НефтеГазПром"',
    'АО',
    'Генеральный директор',
    'Иванов Петр Сергеевич',
    'г. Москва, ул. Ленина, д. 1',
    '+7 (495) 123-45-67',
    'info@ngp.ru',
    'ВХ-01-123456',
    '2024-01-01'
),
-- Вторая организация
(
    'ООО "ХимПром"',
    'Общество с ограниченной ответственностью "ХимПром"',
    'ООО',
    'Директор',
    'Петрова Анна Ивановна',
    'г. Казань, пр. Химиков, д. 10',
    '+7 (843) 234-56-78',
    'office@himprom.ru',
    'ВХ-02-234567',
    '2024-01-15'
),
-- Третья организация
(
    'ПАО "ГазНефтеХим"',
    'Публичное акционерное общество "ГазНефтеХим"',
    'ПАО',
    'Генеральный директор',
    'Сидоров Алексей Владимирович',
    'г. Уфа, ул. Производственная, д. 5',
    '+7 (347) 345-67-89',
    'info@gnhim.ru',
    'ВХ-03-345678',
    '2024-02-01'
);

-- Опасные производственные объекты для первой организации
INSERT INTO dangerous_objects (
    organization_id, name, reg_number, hazard_class,
    location, employee_count
) VALUES
(1, 'Площадка нефтехимического производства', 'А01-12345-0001', 'I',
 'г. Москва, ул. Промышленная, 2', 250),
(1, 'Товарно-сырьевая база', 'А01-12345-0002', 'II',
 'Московская обл., г. Химки, ул. Складская, 1', 120),
(1, 'Установка первичной переработки', 'А01-12345-0003', 'III',
 'г. Москва, ул. Промышленная, 2А', 80);

-- Опасные производственные объекты для второй организации
INSERT INTO dangerous_objects (
    organization_id, name, reg_number, hazard_class,
    location, employee_count
) VALUES
(2, 'Химический комбинат', 'А02-23456-0001', 'I',
 'г. Казань, ул. Химическая, 15', 300),
(2, 'Склад химической продукции', 'А02-23456-0002', 'II',
 'г. Казань, ул. Складская, 10', 75),
(2, 'Производство азотных удобрений', 'А02-23456-0003', 'II',
 'г. Казань, ул. Химическая, 20', 150);

-- Опасные производственные объекты для третьей организации
INSERT INTO dangerous_objects (
    organization_id, name, reg_number, hazard_class,
    location, employee_count
) VALUES
(3, 'Нефтеперерабатывающий завод', 'А03-34567-0001', 'I',
 'г. Уфа, ул. Нефтяников, 1', 400),
(3, 'Резервуарный парк', 'А03-34567-0002', 'II',
 'г. Уфа, ул. Нефтяников, 2', 90),
(3, 'Газоперерабатывающий комплекс', 'А03-34567-0003', 'I',
 'г. Уфа, ул. Промышленная, 5', 280);

-- Проекты для ОПО первой организации
INSERT INTO projects (
    opo_id, name, project_code, dpb_code
) VALUES
-- Для первого ОПО
(1, 'Модернизация установки пиролиза', 'NGP-2024-001', 'DPB-2024-001'),
(1, 'Реконструкция факельного хозяйства', 'NGP-2024-002', 'DPB-2024-002'),
(1, 'Техническое перевооружение компрессорной', 'NGP-2024-003', 'DPB-2024-003'),
-- Для второго ОПО
(2, 'Модернизация системы налива', 'NGP-2024-004', 'DPB-2024-004'),
(2, 'Реконструкция резервуарного парка', 'NGP-2024-005', 'DPB-2024-005'),
(2, 'Техническое перевооружение насосной', 'NGP-2024-006', 'DPB-2024-006'),
-- Для третьего ОПО
(3, 'Модернизация системы автоматизации', 'NGP-2024-007', 'DPB-2024-007'),
(3, 'Реконструкция системы охлаждения', 'NGP-2024-008', 'DPB-2024-008'),
(3, 'Техническое перевооружение установки', 'NGP-2024-009', 'DPB-2024-009');

-- Проекты для ОПО второй организации
INSERT INTO projects (
    opo_id, name, project_code, dpb_code
) VALUES
-- Для первого ОПО
(4, 'Модернизация реакторного блока', 'HIM-2024-001', 'DPB-2024-010'),
(4, 'Реконструкция системы очистки', 'HIM-2024-002', 'DPB-2024-011'),
(4, 'Техническое перевооружение установки синтеза', 'HIM-2024-003', 'DPB-2024-012'),
-- Для второго ОПО
(5, 'Модернизация складского комплекса', 'HIM-2024-004', 'DPB-2024-013'),
(5, 'Реконструкция системы вентиляции', 'HIM-2024-005', 'DPB-2024-014'),
(5, 'Техническое перевооружение погрузочной эстакады', 'HIM-2024-006', 'DPB-2024-015'),
-- Для третьего ОПО
(6, 'Модернизация производства карбамида', 'HIM-2024-007', 'DPB-2024-016'),
(6, 'Реконструкция компрессорной станции', 'HIM-2024-008', 'DPB-2024-017'),
(6, 'Техническое перевооружение узла грануляции', 'HIM-2024-009', 'DPB-2024-018');

-- Проекты для ОПО третьей организации
INSERT INTO projects (
    opo_id, name, project_code, dpb_code
) VALUES
-- Для первого ОПО
(7, 'Модернизация установки каталитического крекинга', 'GNH-2024-001', 'DPB-2024-019'),
(7, 'Реконструкция блока гидроочистки', 'GNH-2024-002', 'DPB-2024-020'),
(7, 'Техническое перевооружение установки риформинга', 'GNH-2024-003', 'DPB-2024-021'),
-- Для второго ОПО
(8, 'Модернизация резервуаров хранения', 'GNH-2024-004', 'DPB-2024-022'),
(8, 'Реконструкция системы пожаротушения', 'GNH-2024-005', 'DPB-2024-023'),
(8, 'Техническое перевооружение насосной станции', 'GNH-2024-006', 'DPB-2024-024'),
-- Для третьего ОПО
(9, 'Модернизация установки осушки газа', 'GNH-2024-007', 'DPB-2024-025'),
(9, 'Реконструкция компрессорного цеха', 'GNH-2024-008', 'DPB-2024-026'),
(9, 'Техническое перевооружение системы очистки', 'GNH-2024-009', 'DPB-2024-027');


-- Вещества
INSERT INTO substances (
    sub_name, class_substance, sub_type,
    density_liquid, molecular_weight,
    boiling_temperature_liquid, heat_evaporation_liquid,
    adiabatic, heat_capacity_liquid, heat_of_combustion,
    sigma, energy_level, flash_point, auto_ignition_temp,
    lower_concentration_limit, upper_concentration_limit,
    threshold_toxic_dose, lethal_toxic_dose
) VALUES
-- ЛВЖ (sub_type = 0)
(
    'Бензин АИ-92', 3, 0,
    750.0, 105.0, 35.0, 295.0,
    1.23, 2.1, 43500.0,
    4, 1, -36.0, 255.0,
    0.76, 5.16, NULL, NULL
),
(
    'Ацетон', 3, 0,
    790.0, 58.08, 56.1, 520.0,
    1.25, 2.16, 31500.0,
    4, 1, -18.0, 465.0,
    2.2, 13.0, NULL, NULL
),
(
    'Толуол', 3, 0,
    866.9, 92.14, 110.6, 425.0,
    1.19, 1.72, 41000.0,
    4, 1, 4.0, 536.0,
    1.3, 6.7, NULL, NULL
),

-- ЛВЖ токсичная (sub_type = 1)
(
    'Метанол', 2, 1,
    791.8, 32.04, 64.7, 1100.0,
    1.21, 2.51, 22700.0,
    4, 1, 6.0, 464.0,
    6.0, 34.7, 1.5, 3.0
),
(
    'Акрилонитрил', 2, 1,
    806.0, 53.06, 77.3, 615.0,
    1.18, 2.09, 31300.0,
    4, 1, -1.0, 481.0,
    3.0, 17.0, 0.5, 1.5
),
(
    'Формальдегид', 2, 1,
    815.0, 30.03, -19.0, 880.0,
    1.27, 2.25, 18700.0,
    4, 1, 56.0, 430.0,
    7.0, 73.0, 0.6, 1.8
),

-- СУГ (sub_type = 2)
(
    'Пропан', 3, 2,
    585.0, 44.1, -42.1, 427.0,
    1.13, 2.42, 46350.0,
    7, 2, -96.0, 466.0,
    2.1, 9.5, NULL, NULL
),
(
    'Бутан', 3, 2,
    600.0, 58.12, -0.5, 385.0,
    1.09, 2.4, 45750.0,
    7, 2, -69.0, 405.0,
    1.8, 9.1, NULL, NULL
),
(
    'Пропилен', 3, 2,
    609.0, 42.08, -47.7, 437.0,
    1.15, 2.46, 45600.0,
    7, 2, -108.0, 455.0,
    2.0, 11.1, NULL, NULL
),

-- СУГ токсичный (sub_type = 3)
(
    'Сероводород', 2, 3,
    960.0, 34.08, -60.3, 548.0,
    1.32, 2.59, 15200.0,
    7, 2, -87.0, 246.0,
    4.3, 45.5, 1.1, 2.8
),
(
    'Аммиак', 2, 3,
    681.9, 17.03, -33.4, 1371.0,
    1.31, 4.52, 18600.0,
    7, 2, -78.0, 651.0,
    15.0, 28.0, 0.7, 2.1
),
(
    'Хлор', 2, 3,
    1470.0, 70.91, -34.1, 289.0,
    1.36, 0.92, NULL,
    7, 2, NULL, NULL,
    NULL, NULL, 0.6, 1.8
),

-- ГЖ (sub_type = 4)
(
    'Дизельное топливо', 4, 4,
    830.0, 170.0, 180.0, 210.0,
    1.02, 2.1, 43500.0,
    4, 1, 35.0, 210.0,
    0.6, 6.5, NULL, NULL
),
(
    'Масло машинное', 4, 4,
    905.0, 400.0, 335.0, 167.0,
    1.05, 1.8, 42000.0,
    4, 1, 210.0, 380.0,
    0.3, 3.0, NULL, NULL
),
(
    'Мазут', 4, 4,
    960.0, 300.0, 250.0, 190.0,
    1.03, 1.9, 41500.0,
    4, 1, 110.0, 350.0,
    0.5, 5.0, NULL, NULL
),

-- ГГ (sub_type = 5)
(
    'Метан', 3, 5,
    NULL, 16.04, -161.5, 510.0,
    1.31, NULL, 50000.0,
    7, 2, NULL, 537.0,
    5.0, 15.0, NULL, NULL
),
(
    'Водород', 3, 5,
    NULL, 2.016, -252.8, 454.0,
    1.41, NULL, 120000.0,
    7, 2, NULL, 510.0,
    4.0, 75.0, NULL, NULL
),
(
    'Этилен', 3, 5,
    NULL, 28.05, -103.7, 483.0,
    1.24, NULL, 47200.0,
    7, 2, NULL, 440.0,
    2.7, 36.0, NULL, NULL
),

-- ГГ токсичный (sub_type = 6)
(
    'Монооксид углерода', 2, 6,
    NULL, 28.01, -191.5, 215.0,
    1.40, NULL, 10100.0,
    7, 2, NULL, 605.0,
    12.5, 74.0, 1.2, 3.6
),
(
    'Синильная кислота', 1, 6,
    NULL, 27.03, 25.7, 933.0,
    1.41, NULL, 21600.0,
    7, 2, NULL, 538.0,
    5.6, 40.0, 0.2, 0.4
),
(
    'Фосген', 1, 6,
    NULL, 98.92, 8.2, 247.0,
    1.39, NULL, NULL,
    7, 2, NULL, NULL,
    NULL, NULL, 0.1, 0.3
),

-- ХОВ (sub_type = 7)
(
    'Серная кислота', 2, 7,
    1840.0, 98.08, 279.6, NULL,
    1.22, 1.42, NULL,
    4, 1, NULL, NULL,
    NULL, NULL, 0.8, 2.4
),
(
    'Азотная кислота', 2, 7,
    1513.0, 63.01, 82.6, NULL,
    1.25, 1.75, NULL,
    4, 1, NULL, NULL,
    NULL, NULL, 1.0, 3.0
),
(
    'Гидроксид натрия', 2, 7,
    2130.0, 40.0, 1388.0, NULL,
    1.18, 1.49, NULL,
    4, 1, NULL, NULL,
    NULL, NULL, 0.7, 2.1
);