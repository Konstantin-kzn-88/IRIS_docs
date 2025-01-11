-- Отключаем проверку внешних ключей на время очистки
PRAGMA foreign_keys = OFF;

-- Очищаем все таблицы
DELETE FROM calculation_results;
DELETE FROM pipelines;
DELETE FROM pumps;
DELETE FROM technological_devices;
DELETE FROM tanks;
DELETE FROM truck_tanks;
DELETE FROM compressors;
DELETE FROM base_equipment;
DELETE FROM substances;
DELETE FROM projects;
DELETE FROM dangerous_objects;
DELETE FROM organizations;

-- Сбрасываем автоинкрементные счетчики
DELETE FROM sqlite_sequence;

-- Включаем обратно проверку внешних ключей
PRAGMA foreign_keys = ON;