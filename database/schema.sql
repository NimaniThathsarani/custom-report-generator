-- =============================================================
--  Custom Report Generator – MySQL Schema
-- =============================================================

CREATE DATABASE IF NOT EXISTS report_generator
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE report_generator;

-- -------------------------------------------------------------
-- 1. PRODUCTS  (shared by Sales + Inventory)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_name    VARCHAR(150)    NOT NULL,
    category        VARCHAR(80)     NOT NULL,
    unit_price      DECIMAL(10, 2)  NOT NULL DEFAULT 0.00,
    reorder_level   INT UNSIGNED    NOT NULL DEFAULT 0,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 2. WAREHOUSES  (Inventory)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    warehouse_name  VARCHAR(100)    NOT NULL UNIQUE,
    location        VARCHAR(150)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 3. INVENTORY  (Inventory Report)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id          INT UNSIGNED    NOT NULL,
    warehouse_id        INT UNSIGNED    NOT NULL,
    current_stock       INT UNSIGNED    NOT NULL DEFAULT 0,
    last_updated        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)    REFERENCES products(product_id)   ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
    UNIQUE KEY uq_product_warehouse (product_id, warehouse_id),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_stock (current_stock)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 4. REGIONS  (Sales Report)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS regions (
    region_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 5. SALES  (Sales Report)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id      INT UNSIGNED    NOT NULL,
    region_id       INT UNSIGNED    NOT NULL,
    sale_date       DATE            NOT NULL,
    quantity_sold   INT UNSIGNED    NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10, 2)  NOT NULL,          -- snapshot at time of sale
    total_amount    DECIMAL(12, 2)  GENERATED ALWAYS AS (quantity_sold * unit_price) STORED,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    FOREIGN KEY (region_id)  REFERENCES regions(region_id)   ON DELETE RESTRICT,
    INDEX idx_sale_date  (sale_date),
    INDEX idx_product    (product_id),
    INDEX idx_region     (region_id),
    INDEX idx_date_range (sale_date, region_id, product_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 6. USERS  (User Activity Report)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(80)     NOT NULL UNIQUE,
    email       VARCHAR(150)    NOT NULL UNIQUE,
    full_name   VARCHAR(150)    NOT NULL,
    role        ENUM('admin','manager','analyst','viewer') NOT NULL DEFAULT 'viewer',
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 7. USER_ACTIVITY  (User Activity Report)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id             INT UNSIGNED    NOT NULL,
    login_date          DATE            NOT NULL,
    login_time          TIME            NOT NULL,
    activity_type       ENUM(
                            'Login',
                            'Logout',
                            'View Report',
                            'Generate Report',
                            'Export Excel',
                            'Export PDF',
                            'Update Settings',
                            'Schedule Report'
                        ) NOT NULL,
    session_duration    SMALLINT UNSIGNED NULL COMMENT 'Duration in minutes; NULL for Logout',
    ip_address          VARCHAR(45)     NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_date     (user_id, login_date),
    INDEX idx_login_date    (login_date),
    INDEX idx_activity_type (activity_type)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- 8. REPORT_SCHEDULES  (Scheduling Feature)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS report_schedules (
    schedule_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED    NOT NULL,
    report_type     ENUM('sales','user_activity','inventory') NOT NULL,
    frequency       ENUM('daily','weekly','monthly') NOT NULL,
    export_format   ENUM('excel','pdf') NOT NULL,
    scheduled_time  TIME            NOT NULL,
    filters_json    JSON            NULL COMMENT 'Stored filter parameters as JSON',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    last_run        TIMESTAMP       NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_active_schedules (is_active, frequency)
) ENGINE=InnoDB;
