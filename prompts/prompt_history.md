# AI Prompt History

## Project: DataFlow Analytics Platform

The following are the main prompts used during the development of this project. They are written in a natural, conversational style to reflect the way I asked for help.

### 1. Understanding the project

**Prompt 1**

Help me understand this Data Engineering assignment. Explain what I need to build and divide the work into simple steps so I can complete it one by one.

**Prompt 2**

I want to build a sales analytics data pipeline using Python and PostgreSQL. Suggest a simple architecture and explain how the different parts will work together.

**Prompt 3**

Help me decide the source tables, target tables, columns, data types, primary keys and foreign keys for this project.

### 2. Environment and database setup

**Prompt 4**

Guide me through setting up this project on Windows using VS Code. Give me the commands one by one and explain what each command does.

**Prompt 5**

Help me set up PostgreSQL using Docker Compose and connect it to my Python project. I want to understand the configuration instead of just copying it.

**Prompt 6**

Create the PostgreSQL schema for my sales analytics project. Include customer, product, date, sales, pipeline run and rejected records tables with suitable constraints and indexes.

### 3. Sample data and ingestion

**Prompt 7**

Help me generate sample customer and order data using Python. I need a fixed random seed so that I get the same data whenever I run the generator. It should also support generating a larger dataset.

**Prompt 8**

Help me write Python code to load customer data from a JSON file and order data from a CSV file using Pandas. Please explain the code step by step.

### 4. Data validation and transformation

**Prompt 9**

Help me validate customer records. I need to identify missing required fields, blank values and duplicate customer IDs, and separate valid records from rejected ones.

**Prompt 10**

Help me validate order records. Check missing fields, duplicate order line IDs, invalid customer and product references, quantities, prices, dates and order statuses.

**Prompt 11**

After validation, help me calculate the total amount for each order line and prepare the valid records for loading into the warehouse.

### 5. Warehouse loading and reliability

**Prompt 12**

Help me load the validated data into PostgreSQL using batch inserts. I want to use dimension tables and a sales fact table.

**Prompt 13**

I need to run the pipeline multiple times without inserting duplicate sales records. Help me implement this safely using PostgreSQL upserts or conflict handling.

**Prompt 14**

Help me track every pipeline execution with its status, start time, end time, source count, valid count, rejected count and error details.

**Prompt 15**

I also need to store rejected records with their original data and rejection reasons so I can investigate data quality issues later.

### 6. SQL analytics and reconciliation

**Prompt 16**

Help me write SQL queries to analyse monthly sales, product category performance, top customers, customer segments and order statuses.

**Prompt 17**

Help me write reconciliation queries to verify record counts, duplicate records, incorrect sales amounts and missing foreign key references.

### 7. Testing and performance

**Prompt 18**

Help me write pytest test cases for the customer and order validators. Include normal cases, missing values, duplicates and invalid data.

**Prompt 19**

My pytest command is showing an import error. Help me understand why it is happening and fix it without changing the project architecture unnecessarily.

**Prompt 20**

Help me measure the pipeline execution time. I want to compare the original batch size with a larger batch size and document whether performance improved.

### 8. Documentation

**Prompt 21**

Help me prepare the architecture document and data dictionary for this project. Keep the explanation clear and make sure it matches the actual database schema.

**Prompt 22**

Help me write a README with project setup instructions, dependencies, commands to run the pipeline, testing steps and known limitations.

## How I Used AI Assistance

I used AI assistance mainly when I needed help understanding a requirement, planning the project structure, writing initial code, debugging errors and preparing documentation.

I reviewed the suggested code and made changes wherever needed. I also ran the application locally, checked the database records, tested invalid inputs, reran the pipeline and verified the results using SQL queries.

I used the suggestions as guidance rather than accepting everything without checking it. I made sure I could understand the main parts of the implementation and explain the decisions behind them.

## Validation I Performed

- Generated 10,000 customer records and 100,000 order records.
- Checked that the ingestion modules loaded the expected data.
- Tested customer and order validation rules.
- Ran the pipeline multiple times to check duplicate prevention.
- Inserted an invalid record and verified that it was stored with its rejection reason.
- Checked the warehouse using SQL reconciliation queries.
- Ran the automated test suite and confirmed that all 22 tests passed.
- Compared pipeline execution time before and after increasing the batch size.

## My Responsibility

AI assistance helped me during development, but I am responsible for the final implementation. I reviewed the code, tested the functionality and checked the output before including it in the project. I will also be able to explain the implementation, its assumptions and its limitations.