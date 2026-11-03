
-- DataFlow Analytics Platform
-- PostgreSQL dimensional data warehouse schema

-- 1. CUSTOMER DIMENSION
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    customer_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. PRODUCT DIMENSION
CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. DATE DIMENSION
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
    day_of_week VARCHAR(20) NOT NULL
);

-- 4. SALES FACT TABLE
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_line_id VARCHAR(100) NOT NULL UNIQUE,

    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    date_key INTEGER NOT NULL,

    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(14, 2) NOT NULL CHECK (total_amount >= 0),

    order_status VARCHAR(30) NOT NULL,
    source_file VARCHAR(255),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT chk_sales_total
        CHECK (total_amount = quantity * unit_price)
);

-- 5. PIPELINE RUN TRACKING
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_status VARCHAR(20) NOT NULL
        CHECK (run_status IN ('RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL')),

    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,

    source_records INTEGER NOT NULL DEFAULT 0,
    valid_records INTEGER NOT NULL DEFAULT 0,
    rejected_records INTEGER NOT NULL DEFAULT 0,
    inserted_records INTEGER NOT NULL DEFAULT 0,

    error_message TEXT
);

-- 6. REJECTED RECORDS
CREATE TABLE IF NOT EXISTS rejected_records (
    rejection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id BIGINT NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    source_record_id VARCHAR(100),
    raw_record JSONB NOT NULL,
    rejection_reason TEXT NOT NULL,

    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rejected_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
);

-- INDEXES FOR COMMON ANALYTICAL QUERIES
CREATE INDEX IF NOT EXISTS idx_sales_customer
    ON fact_sales(customer_key);

CREATE INDEX IF NOT EXISTS idx_sales_product
    ON fact_sales(product_key);

CREATE INDEX IF NOT EXISTS idx_sales_date
    ON fact_sales(date_key);

CREATE INDEX IF NOT EXISTS idx_sales_status
    ON fact_sales(order_status);

CREATE INDEX IF NOT EXISTS idx_rejected_run
    ON rejected_records(run_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_status
    ON pipeline_runs(run_status);
