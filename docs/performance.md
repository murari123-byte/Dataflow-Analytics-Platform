
# Performance Benchmarking

## Test Environment
- Language: Python 3.13
- Database: PostgreSQL 16
- Dataset: 10,000 customers and 100,000 order records
- Execution: Local Windows environment using Docker

## Optimization

The original database insertion batch size was 1,000 records.

It was increased to 5,000 records to reduce the number of database execution batches and associated overhead.

## Benchmark Results

| Metric | Before | After |
|---|---:|---:|
| Batch size | 1,000 | 5,000 |
| Execution time | 10.23 sec | 8.99 sec |
| Sales records | 100,000 | 100,000 |

## Performance Improvement

Execution time decreased by 1.24 seconds.

Percentage improvement:

(10.23 - 8.99) / 10.23 * 100 = 12.12%

## Conclusion

Increasing the database insertion batch size from 1,000
to 5,000 improved the measured pipeline execution time
by approximately 12.12%.

The warehouse retained all 100,000 sales records without
creating duplicates.

Note: These are single-run measurements in a local
development environment, not production performance guarantees.
