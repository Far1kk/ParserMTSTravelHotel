-- Таблица Регионы
CREATE TABLE regions (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    name VARCHAR(255) NOT NULL,    -- Наименование региона
    external_id VARCHAR(255)        -- Внешний идентификатор
);

-- Таблица Конкуренты
CREATE TABLE competitors (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    name VARCHAR(255) NOT NULL,     -- Наименование конкурента
    weight FLOAT,                   -- Вес конкурента
    url VARCHAR(255)                -- URL конкурента
);

-- Таблица Регионов Конкурентов
CREATE TABLE regions_competitors (
    region_id INT REFERENCES regions(id) ON DELETE CASCADE,  -- Идентификатор региона
    competitor_id INT REFERENCES competitors(id) ON DELETE CASCADE,  -- Идентификатор конкурента
    url VARCHAR(500),              -- URL адрес
    PRIMARY KEY (region_id, competitor_id)  -- Составной первичный ключ
);

-- Таблица Отели Конкурентов
CREATE TABLE competitor_hotels (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    external_id VARCHAR(255),       -- Внешний идентификатор
    name VARCHAR(255) NOT NULL,     -- Наименование отеля
    url VARCHAR(500),               -- URL адрес
    address VARCHAR(255),           -- Адрес
    region_id INT REFERENCES regions(id) ON DELETE SET NULL,  -- Идентификатор региона
    parsing_date DATE               -- Дата парсинга
);

-- Таблица Ценовые Сегменты
CREATE TABLE price_segments (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    name VARCHAR(255) NOT NULL,     -- Название
    price_from DECIMAL(10, 2),      -- Цена от
    price_to DECIMAL(10, 2)         -- Цена до
);

-- Таблица Номера Отелей Конкурентов
CREATE TABLE competitor_hotel_rooms (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    external_id VARCHAR(255),       -- Внешний идентификатор
    hotel_id INT REFERENCES competitor_hotels(id) ON DELETE CASCADE,  -- Идентификатор отеля
    name VARCHAR(255) NOT NULL,     -- Наименование номера
    price_segment_id int REFERENCES price_segments(id) ON DELETE SET NULL,     -- Ценовой сегмент
    wifi_flag BOOLEAN,              -- Флаг wifi
    shower_flag BOOLEAN,            -- Флаг душа
    capacity INT,                   -- Вместительность номера
    parsing_date DATE                -- Дата парсинга
);

-- Таблица Цены Номеров Отелей Конкурентов
CREATE TABLE competitor_room_prices (
    room_id INT REFERENCES competitor_hotel_rooms(id) ON DELETE CASCADE,  -- Идентификатор номера
    start_date DATE NOT NULL,       -- Дата старта цены
    end_date DATE,                  -- Дата окончания цены
    price DECIMAL(10, 2) NOT NULL,  -- Цена
    recalculation_date timestamp,         -- Дата перерасчета
    PRIMARY KEY (room_id, start_date)  -- Составной первичный ключ
	-- Сделать валидацию на пересечения дат для номера
);

-- Таблица Отели Компании
CREATE TABLE company_hotels (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    external_id VARCHAR(255),       -- Внешний идентификатор
    name VARCHAR(255) NOT NULL,     -- Наименование отеля
    address VARCHAR(255),           -- Адрес
    region_id INT REFERENCES regions(id) ON DELETE SET NULL  -- Идентификатор региона
);

-- Таблица Номера Отелей Компании
CREATE TABLE company_hotel_rooms (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,          -- Автоинкрементируемый идентификатор
    external_id VARCHAR(255),       -- Внешний идентификатор
    hotel_id INT REFERENCES company_hotels(id) ON DELETE CASCADE,  -- Идентификатор отеля
    name VARCHAR(255) NOT NULL,     -- Наименование номера
    price_segment_id int REFERENCES price_segments(id) ON DELETE SET NULL,     -- Ценовой сегмент
    wifi_flag BOOLEAN,              -- Флаг wifi
    shower_flag BOOLEAN,            -- Флаг душа
    capacity INT                    -- Вместительность номера
);

-- Таблица Аналоги Отелей
CREATE TABLE hotel_analogs (
    company_hotel_id INT REFERENCES company_hotels(id) ON DELETE CASCADE,  -- Идентификатор отеля компании
    competitor_hotel_id INT REFERENCES competitor_hotels(id) ON DELETE CASCADE,  -- Идентификатор отеля конкурента
    weight FLOAT,                 -- Вес аналога
    PRIMARY KEY (company_hotel_id, competitor_hotel_id)  -- Составной первичный ключ
);

-- Таблица Аналоги Номеров
CREATE TABLE room_analogs (
    company_room_id INT REFERENCES company_hotel_rooms(id) ON DELETE CASCADE,  -- Идентификатор номера компании
    competitor_room_id INT REFERENCES competitor_hotel_rooms(id) ON DELETE CASCADE,  -- Идентификатор номера конкурента
    weight FLOAT,                 -- Вес аналога
    PRIMARY KEY (company_room_id, competitor_room_id)  -- Составной первичный ключ
);