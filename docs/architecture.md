
# DataFlow Analytics Platform – Architecture

## 1. Project Overview

DataFlow Analytics Platform is a Python-based data engineering pipeline that ingests customer and order data, validates records, transforms valid data and loads it into a PostgreSQL dimensional warehouse.

The platform supports repeatable execution, data quality checks, rejection tracking, monitoring and analytical reporting.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.13 |
| Data Processing | Pandas |
| Database | PostgreSQL 16 |
| Database Connectivity | SQLAlchemy, Psycopg |
| Containerization | Docker |
| Testing | Pytest |
| Query Language | SQL |

## 3. Data Sources

### Customers
- File: data/raw/customers.json
- Format: JSON
- Contains customer details such as ID, name, email, location and segment.

### Orders
- File: data/raw/orders.csv
- Format: CSV
- Contains order details, product information, quantities, prices and order status.

## 4. Pipeline Architecture

The pipeline follows these stages:

1. Data Generation
   - Generate reproducible synthetic customer and order records.
   - Use a fixed random seed.

2. Data Ingestion
   - Read customer JSON and order CSV files.
   - Convert source records into Pandas DataFrames.

3. Data Validation
   - Check required fields and duplicate identifiers.
   - Validate customer and product references.
   - Validate quantities, prices, dates and order statuses.

4. Rejection Handling
   - Separate invalid records from valid records.
   - Store rejected records with their source information and rejection reasons.

5. Data Transformation
   - Calculate order-line totals.
   - Prepare dimension attributes.
   - Map business identifiers to warehouse surrogate keys.

6. Data Loading
   - Load customer, product and date dimensions.
   - Load sales transactions into the fact table.
   - Use database transactions and conflict handling to support safe reruns.

7. Monitoring
   - Track pipeline execution status.
   - Store source, valid, rejected and inserted record counts.
   - Capture errors for failed executions.

8. Analytics
   - Generate business reports using SQL queries.

## 5. Dimensional Data Model

The warehouse follows a star schema.

### Dimension Tables

- dim_customer: Customer information.
- dim_product: Product information.
- dim_date: Calendar information.

### Fact Table

- fact_sales: Sales transactions, quantities, prices, amounts and dimension references.

### Monitoring Tables

- pipeline_runs: Pipeline execution history.
- rejected_records: Invalid source records and rejection reasons.

## 6. Architecture Flow

Source Files
    |
    v
Data Ingestion
    |
    v
Data Validation
    |
    +--------------------+
    |                    |
    v                    v
Valid Records       Rejected Records
    |                    |
    v                    v
Transformation      Rejection Storage
    |
    v
PostgreSQL Warehouse
    |
    v
SQL Analytics Reports

Pipeline execution details are tracked separately in pipeline_runs.

## 7. Reliability Features

- Idempotent fact loading using order_line_id.
- Database transactions for warehouse loading.
- Rejected record tracking.
- Pipeline execution monitoring.
- Automated validation tests.
- Fixed-seed synthetic data generation.

## 8. Scalability

The data generator supports larger datasets through configurable customer and order counts.

Database inserts are performed in batches. The batch size was increased from 1,000 to 5,000 during performance testing.
