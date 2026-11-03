
# DataFlow Analytics Platform – Data Dictionary

## 1. Overview

The DataFlow Analytics Platform uses a PostgreSQL dimensional data warehouse based on a star schema.

The database contains six tables:
- dim_customer
- dim_product
- dim_date
- fact_sales
- pipeline_runs
- rejected_records

The first four tables support sales analytics. The remaining two tables support pipeline monitoring and data quality tracking.

## 2. Customer Dimension – dim_customer

Stores customer information.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| customer_key | BIGINT | Primary Key, Identity | Unique warehouse customer key |
| customer_id | VARCHAR(50) | NOT NULL, UNIQUE | Source customer identifier |
| customer_name | VARCHAR(150) | NOT NULL | Customer name |
| email | VARCHAR(255) | NULL | Customer email |
| city | VARCHAR(100) | NULL | Customer city |
| state | VARCHAR(100) | NULL | Customer state |
| country | VARCHAR(100) | NULL | Customer country |
| customer_segment | VARCHAR(50) | NULL | Customer business segment |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

## 3. Product Dimension – dim_product

Stores product information.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| product_key | BIGINT | Primary Key, Identity | Unique warehouse product key |
| product_id | VARCHAR(50) | NOT NULL, UNIQUE | Source product identifier |
| product_name | VARCHAR(150) | NOT NULL | Product name |
| category | VARCHAR(100) | NULL | Product category |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

## 4. Date Dimension – dim_date

Stores calendar attributes for analytical reporting.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| date_key | INTEGER | Primary Key | Date identifier in YYYYMMDD format |
| full_date | DATE | NOT NULL, UNIQUE | Actual calendar date |
| year | INTEGER | NOT NULL | Calendar year |
| quarter | INTEGER | NOT NULL, CHECK 1–4 | Calendar quarter |
| month | INTEGER | NOT NULL, CHECK 1–12 | Calendar month |
| month_name | VARCHAR(20) | NOT NULL | Month name |
| day | INTEGER | NOT NULL, CHECK 1–31 | Day of month |
| day_of_week | VARCHAR(20) | NOT NULL | Weekday name |

## 5. Sales Fact – fact_sales

Stores individual order-line transactions and references the dimension tables.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| sales_key | BIGINT | Primary Key, Identity | Unique warehouse sales key |
| order_id | VARCHAR(50) | NOT NULL | Source order identifier |
| order_line_id | VARCHAR(100) | NOT NULL, UNIQUE | Unique order-line identifier |
| customer_key | BIGINT | NOT NULL, Foreign Key | References dim_customer |
| product_key | BIGINT | NOT NULL, Foreign Key | References dim_product |
| date_key | INTEGER | NOT NULL, Foreign Key | References dim_date |
| quantity | INTEGER | NOT NULL, CHECK > 0 | Number of units purchased |
| unit_price | NUMERIC(12,2) | NOT NULL, CHECK >= 0 | Price per unit |
| total_amount | NUMERIC(14,2) | NOT NULL, CHECK >= 0 | Quantity multiplied by unit price |
| order_status | VARCHAR(30) | NOT NULL | Order status |
| source_file | VARCHAR(255) | NULL | Original source filename |
| loaded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Warehouse loading timestamp |

### Sales Fact Relationships

- customer_key references dim_customer.customer_key.
- product_key references dim_product.product_key.
- date_key references dim_date.date_key.
- order_line_id must be unique.
- total_amount must equal quantity multiplied by unit_price.

## 6. Pipeline Run Tracking – pipeline_runs

Stores execution details for every pipeline run.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| run_id | BIGINT | Primary Key, Identity | Unique pipeline execution ID |
| run_status | VARCHAR(20) | NOT NULL, CHECK | Execution status |
| start_time | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Pipeline start time |
| end_time | TIMESTAMP | NULL | Pipeline completion time |
| source_records | INTEGER | NOT NULL, DEFAULT 0 | Total source records |
| valid_records | INTEGER | NOT NULL, DEFAULT 0 | Valid records |
| rejected_records | INTEGER | NOT NULL, DEFAULT 0 | Rejected records |
| inserted_records | INTEGER | NOT NULL, DEFAULT 0 | Newly inserted sales records |
| error_message | TEXT | NULL | Failure details, if any |

Allowed run statuses:
- RUNNING
- SUCCESS
- FAILED
- PARTIAL

## 7. Rejected Records – rejected_records

Stores source records that fail validation.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| rejection_id | BIGINT | Primary Key, Identity | Unique rejection identifier |
| run_id | BIGINT | NOT NULL, Foreign Key | References pipeline_runs |
| source_file | VARCHAR(255) | NOT NULL | Original source filename |
| source_record_id | VARCHAR(100) | NULL | Source record identifier |
| raw_record | JSONB | NOT NULL | Original rejected record |
| rejection_reason | TEXT | NOT NULL | Reason for rejection |
| rejected_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Rejection timestamp |

## 8. Database Indexes

The following indexes support common queries and lookups.

| Index Name | Table | Column |
|---|---|---|
| idx_sales_customer | fact_sales | customer_key |
| idx_sales_product | fact_sales | product_key |
| idx_sales_date | fact_sales | date_key |
| idx_sales_status | fact_sales | order_status |
| idx_rejected_run | rejected_records | run_id |
| idx_pipeline_status | pipeline_runs | run_status |

## 9. Business Rules

1. Customer IDs must be unique.
2. Product IDs must be unique.
3. Order-line IDs must be unique.
4. Customer, product and date references must exist in their respective dimension tables.
5. Quantity must be a positive integer.
6. Unit price must be greater than or equal to zero.
7. Total amount must equal quantity multiplied by unit price.
8. Order dates must be valid.
9. Order statuses must be COMPLETED, PENDING or CANCELLED.
10. Invalid source records must be stored with their rejection reasons.
11. Repeated pipeline executions must not create duplicate sales transactions.

## 10. Data Model Summary

The warehouse follows a star schema:

- dim_customer, dim_product and dim_date are dimension tables.
- fact_sales is the central fact table.
- pipeline_runs and rejected_records provide operational monitoring and data quality tracking.

The fact table stores sales at the individual order-line level.
