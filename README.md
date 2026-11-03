# DataFlow Analytics Platform

A Python and PostgreSQL-based data engineering project that ingests customer and order data, validates records, transforms the data and loads it into a dimensional data warehouse for sales analytics.

## 1. Project Overview

The DataFlow Analytics Platform is designed to demonstrate an end-to-end data engineering workflow.

It processes customer information from a JSON source and sales order information from a CSV source. The pipeline performs data validation, handles rejected records, transforms valid data and loads it into PostgreSQL.

The warehouse follows a star schema, making it easier to perform analytical queries and generate sales reports.

## 2. Key Features

- Ingest customer data from JSON files.
- Ingest order data from CSV files.
- Generate reproducible synthetic datasets using a fixed random seed.
- Validate incoming records and identify data quality issues.
- Separate valid and rejected records.
- Store rejected records with their original data and rejection reasons.
- Transform data and calculate sales amounts.
- Load data into PostgreSQL dimensional tables.
- Use batch inserts and conflict handling to prevent duplicate sales records.
- Track pipeline execution status and record counts.
- Perform data reconciliation checks.
- Generate SQL-based sales analytics.
- Run automated tests using Pytest.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas |
| Database | PostgreSQL |
| Database Connectivity | SQLAlchemy, Psycopg |
| Containerization | Docker, Docker Compose |
| Configuration | Python-dotenv |
| Testing | Pytest |
| Analytics | SQL |
| Version Control | Git, GitHub |


## 4. Project Structure

```text
dataflow-analytics-platform/
│
├── data/
│   └── raw/
│       ├── customers.json
│       └── orders.csv
│
├── src/
│   ├── ingestion/
│   │   ├── customer_loader.py
│   │   ├── order_loader.py
│   │   └── __init__.py
│   │
│   ├── validation/
│   │   ├── customer_validator.py
│   │   ├── order_validator.py
│   │   └── __init__.py
│   │
│   ├── loading/
│   │   ├── database.py
│   │   ├── load_warehouse.py
│   │   └── __init__.py
│   │
│   ├── test_connection.py
│   └── __init__.py
│
├── scripts/
│   └── generate_data.py
│
├── sql/
│   ├── schema.sql
│   ├── analytics.sql
│   └── reconciliation.sql
│
├── tests/
│   ├── conftest.py
│   ├── test_validators.py
│   └── test_ingestion.py
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── performance.md
│
├── prompts/
│   └── prompt_history.md
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```


## 5. Database Design

The project uses a dimensional data warehouse based on a star schema.

### Dimension Tables

- **dim_customer:** Stores customer details.
- **dim_product:** Stores product information.
- **dim_date:** Stores calendar and date-related information.

### Fact Table

- **fact_sales:** Stores sales transaction details, including order information, customer and product references, quantity, unit price and total amount.

### Pipeline Monitoring Tables

- **pipeline_runs:** Tracks pipeline execution status, timestamps and processing counts.
- **rejected_records:** Stores invalid records with their source information and rejection reasons.

Primary keys, foreign keys, unique constraints, check constraints and indexes are used to maintain data integrity.

For more details, see [Data Dictionary](docs/data_dictionary.md).

## 6. Setup Instructions

Follow these steps to set up the project on a Windows machine.

### Prerequisites

Install the following:

- Python 3.10 or later.
- Docker Desktop.
- Git.
- Visual Studio Code (recommended).

### Step 1: Clone the Repository

```powershell
git clone https://github.com/murari123-byte/Dataflow-Analytics-Platform.git
```

Navigate to the project folder:

```powershell
cd dataflow-analytics-platform
```

### Step 2: Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a reference.

Example configuration:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=dataflow_db
DB_USER=dataflow_user
DB_PASSWORD=your_local_database_password
```

Use the same database credentials in your Docker Compose configuration. Keep `.env` private and never commit it to GitHub.

### Step 5: Start PostgreSQL Using Docker

Make sure Docker Desktop is running.

Start the database container:

```powershell
docker compose up -d
```

Check the container status:

```powershell
docker compose ps
```

Wait until the PostgreSQL container is healthy.

### Step 6: Create the Database Schema

Execute the SQL schema file:

```powershell
Get-Content .\sql\schema.sql -Raw | docker exec -i dataflow_postgres psql -U dataflow_user -d dataflow_db
```

This creates the required dimension, fact and pipeline monitoring tables.

### Step 7: Verify Database Connection

Run:

```powershell
python src/test_connection.py
```

A successful connection should display a database connection confirmation and PostgreSQL version.

## 7. Running the Complete Pipeline

Run all commands from the project root directory with the virtual environment activated.

### Step 1: Generate Sample Data

```powershell
python scripts/generate_data.py
```

By default, the generator creates:

- 10,000 customer records.
- 100,000 order records.

The generator uses a fixed random seed to make the dataset reproducible.

To generate a larger dataset:

```powershell
python scripts/generate_data.py --customers 50000 --orders 500000
```

### Step 2: Execute the Data Pipeline

```powershell
python -m src.loading.load_warehouse
```

The pipeline performs the following operations:

1. Reads customer JSON and order CSV files.
2. Validates incoming records.
3. Separates valid and rejected records.
4. Saves rejected records in PostgreSQL.
5. Loads customer, product and date dimensions.
6. Loads valid sales records into the fact table.
7. Records pipeline execution details.

### Step 3: Run Automated Tests

```powershell
python -m pytest -v
```

The automated test suite currently contains 32 tests:
- 22 customer and order validation tests.
- 7 ingestion tests covering empty files, malformed JSON, incorrect JSON structure and missing files.

### Step 4: Run Data Reconciliation Checks

```powershell
Get-Content .\sql\reconciliation.sql -Raw | docker exec -i dataflow_postgres psql -U dataflow_user -d dataflow_db
```

The reconciliation queries check:

- Pipeline record counts.
- Duplicate sales records.
- Incorrect sales calculations.
- Missing foreign key references.
- Rejected record counts.

### Step 5: Run Sales Analytics

```powershell
Get-Content .\sql\analytics.sql -Raw | docker exec -i dataflow_postgres psql -U dataflow_user -d dataflow_db
```

The analytics queries cover:

1. Monthly sales performance.
2. Revenue by product category.
3. Top customers by revenue.
4. Sales by customer segment.
5. Order status distribution.
6. Overall sales summary.
7. Completed sales revenue.

## 8. Verify Database Records

Connect to PostgreSQL:

```powershell
docker exec -it dataflow_postgres psql -U dataflow_user -d dataflow_db
```

List the database tables:

```sql
\dt
```

Check the number of records:

```sql
SELECT COUNT(*) FROM dim_customer;
SELECT COUNT(*) FROM dim_product;
SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM fact_sales;
SELECT COUNT(*) FROM pipeline_runs;
SELECT COUNT(*) FROM rejected_records;
```

Exit PostgreSQL:

```sql
\q
```

## 9. Data Quality and Business Rules

The pipeline applies the following validation rules:

### Customer Validation

- Customer ID is required.
- Customer name is required.
- Blank required values are rejected.
- Duplicate customer IDs are rejected.

### Order Validation

- Required order fields must be present.
- Duplicate order line IDs are rejected.
- Customer references must exist.
- Product IDs must match the supported product catalogue.
- Quantity must be a positive integer.
- Unit price must be non-negative.
- Order date must be valid.
- Order status must be supported.
- Total amount is calculated using quantity multiplied by unit price.

Invalid records are separated from valid records and stored with their rejection reasons.

## 10. Idempotency and Pipeline Reliability

The pipeline is designed to support repeated execution without creating duplicate sales records.

- Customer and product dimensions use conflict handling and upserts.
- Date dimension records use conflict handling.
- Sales fact records use the unique order line ID to prevent duplicate inserts.
- Each execution is recorded in the pipeline monitoring table.
- Rejected records are stored separately for traceability.

The pipeline can be rerun using the same source data without increasing the fact table's record count.

## 11. Performance Measurement

The pipeline was benchmarked using the generated dataset containing 100,000 order records.

| Configuration | Batch Size | Execution Time |
|---|---:|---:|
| Initial | 1,000 | 10.23 seconds |
| Optimized | 5,000 | 8.99 seconds |

The larger batch size reduced the measured execution time by approximately 12.12% in this local test.

These results are from a single local benchmark and may vary depending on hardware and database conditions.

For details, see [Performance Report](docs/performance.md).

## 12. Testing Results

The automated test suite contains 32 tests in total:

- Valid customer and order records.
- Missing required fields.
- Blank values.
- Duplicate customer IDs.
- Duplicate order line IDs.
- Invalid customer and product references.
- Invalid quantities.
- Fractional quantities.
- Negative and zero prices.
- Invalid dates and order statuses.
- Empty datasets.
- Missing columns.
- Multiple validation errors.
- Empty customer and order input files.
- Malformed JSON, incorrect JSON structure and missing source files.
- Unexpected columns in customer and order source files.
- Late-arriving orders with older dates.

**Latest verified result: 32 tests passed.**

Additional reliability checks performed:
- Re-ran the pipeline to verify that duplicate sales records were not inserted.
- Simulated a warehouse loading failure and verified that the transaction was rolled back.
- Confirmed that the failed run was recorded with its error message.
- Re-ran the pipeline successfully after the failure.
- Verified that the fact_sales table remained at 100,000 records after recovery.

## 13. Assumptions and Limitations

- The project uses synthetic customer and order data.
- The supported product catalogue currently contains 10 predefined products.
- Product validation uses predefined product IDs.
- Customer dimension records maintain the latest customer attributes; historical SCD Type 2 tracking is not implemented.
- Analytics are provided through SQL queries rather than a dashboard.
- Automated tests cover validation and ingestion. Warehouse failure rollback and recovery have also been verified manually; automated database integration tests can be added in future improvements.
- Pipeline monitoring records execution status, but a failure between warehouse commit and final status update can result in a status that does not fully reflect the committed data.

## 14. Project Documentation

Additional documentation is available in the `docs/` directory:

- [Architecture](docs/architecture.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Performance Report](docs/performance.md)

AI assistance and the main development prompts are documented in:

- [AI Prompt History](prompts/prompt_history.md)

## 15. AI Assistance Disclosure

AI assistance was used during project development for understanding requirements, planning the architecture, implementation guidance, debugging, testing ideas and documentation.

The suggested solutions were reviewed and adapted during development. The pipeline was executed locally, database outputs were checked, reconciliation queries were run and automated tests were performed.

The final implementation, design decisions and validation remain my responsibility.

## 16. Stopping the Project

To stop the PostgreSQL container without deleting stored database data:

```powershell
docker compose down
```

To start it again later:

```powershell
docker compose up -d
```

**Important:** Avoid `docker compose down -v` unless you intentionally want to delete the PostgreSQL data volume.