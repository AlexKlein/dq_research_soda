# Research of Data Quality tools. SODA

This project delves into the features offered by the SODA data quality tool.

## Description

This repository consists of:

```markdown
- a database with:
    - a generic table;
    - a table dedicated to SODA results;
- a SODA setup;
- an Airflow setup:
    - a DAG for creating a DB object;
    - a DAG specifically for executing SODA;
- necessary Docker files to containerize the tool.
```

## Airflow
The chosen scheduler for this project is `Airflow v2`. For local access, navigate to [web page](http://localhost:8080/home/). Credentials are stored in the [entrypoint.sh](./project/entrypoint.sh) file.

## Build and Run

When you need to start the app with all infrastructure, you have to make this steps:
1. Modify the environment variables in [YML-file](./project/docker-compose.yml) and [entrypoint.sh](./project/entrypoint.sh) (now there are default values) 
2. Run the following: docker-compose up -d --build command. Give it some time. Your app, tables, and Airflow will soon be ready.

### Note

The database and Airflow webserver need a moment. Once up, proceed with the application.

## List of tables

```sql
-- Automotive Data
select * from automotive.cars;

-- Data Quality Results
select * from data_quality.soda_scan_summary;
```

## Potential improvements

- Develop a mechanism to scan database metadata and execute SODA across all tables.
- Develop a feature for data profiling or for generating standard checks such as `not_null` or `numeric_values_only`.

## Documentation

For a deeper understanding and detailed instructions on SODA, please refer to the official [SODA Documentation](https://docs.soda.io/soda-core/overview-main.html).
