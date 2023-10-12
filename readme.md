# Research of Data Quality tools. SODA

In this project I wanted to explore features of SODA tool.

## Description

This repository consists of:

```
- a database with:
    - a generic table;
    - a table with SODA results;
- a SODA setup;
- an Airflow setup with a DAG for running SODA;
- Docker files for wrapping this tool.
```

## Airflow
As the scheduler I choose Airflow v2. You can get local access there using http://localhost:8080/home/ (credentials you can find in `entrypoint.sh`).

## Build

When you need to start the app with all infrastructure, you have to make this steps:
1. Change environment variables in [YML-file](./project/docker-compose.yml) and [entrypoint.sh](./project/entrypoint.sh) (now there are default values) 
2. Execute the `docker-compose up -d --build` command - in this step the app will be built, tables will be created and Airflow app will be ready in some time.

### Note

You should wait a couple of minutes for the database and Airflow webserer start. After that you may run the application and check logs as the next step.

## Potential improvements

- Create a mechanism which reads DB metadata and runs SODA through all tables.
- Create a mechanism for data profiling or for creating generic checks like `not_null` or `numeric_values_only`.
