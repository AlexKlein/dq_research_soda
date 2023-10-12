import os
import psycopg2
from sqlalchemy.engine.url import make_url
from soda.scan import Scan

# Constants
SCAN_DEFINITION_NAME = "my_dq_scan"
DATA_SOURCE_NAME = "my_small_dwh"
CONFIGURATION_YAML = "configuration.yml"
TABLES_DIR = "/opt/airflow/soda_checks/tables"
LOGS_VERBOSE = False
INCLUDE_PASSED_CHECKS = True
SCAN_SUMMARY_TABLE_NAME = "automotive.soda_scan_summary"


def create_database_connection():
    """Create a connection to the PostgreSQL database using an environment variable."""

    conn_str = os.environ.get("MY_SMALL_DWH_SQL_ALCHEMY_CONN")
    if not conn_str:
        raise ValueError("Environment variable MY_SMALL_DWH_SQL_ALCHEMY_CONN not found!")

    url = make_url(conn_str)

    conn = psycopg2.connect(
        dbname=url.database,
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port
    )

    return conn


def execute_sql_statements(sql_statements):
    """Execute the provided SQL statements using PostgreSQL client."""
    conn = create_database_connection()
    cur = conn.cursor()
    results = []

    for statement in sql_statements:
        try:
            cur.execute(statement)
            results.append({"statement": statement, "status": "SUCCESS"})
        except Exception as e:
            results.append({"statement": statement, "status": str(e)})

    conn.commit()
    cur.close()
    conn.close()

    return results


def parse_checks(logs):
    """Parse the logs to extract relevant data about checks."""
    lines = logs.split("\n")
    parsed_data = []

    table_parts, connection_name = None, None

    for index, line in enumerate(lines):
        if "`" in line and "in" in line and not ("[PASSED]" in line or "[FAILED]" in line):
            parts = line.split("`")[1].split(".")
            if len(parts) == 1:
                table_name, dataset_name, project_name = parts[0], "NULL", "NULL"
            elif len(parts) == 2:
                table_name, dataset_name, project_name = parts[1], parts[0], "NULL"
            else:  # len(parts) == 3
                table_name, dataset_name, project_name = parts[2], parts[1], parts[0]

            connection_name = line.split("in")[1].strip()
        elif "[PASSED]" in line or "[FAILED]" in line:
            check_name = line.split("INFO   |")[1].split("[")[0].strip()
            status = "PASSED" if "[PASSED]" in line else "FAILED"

            additions = "NULL"
            if index + 1 < len(lines) and ("value:" in lines[index + 1] or "check_value:" in lines[index + 1]):
                additions = lines[index + 1].split("INFO   |")[1].strip()

            parsed_data.append((project_name, dataset_name, table_name, connection_name, check_name, status, additions))

    return parsed_data


def generate_sql_inserts(parsed_data):
    """Generate SQL INSERT statements based on parsed data."""
    create_table = f"""
    CREATE TABLE IF NOT EXISTS {SCAN_SUMMARY_TABLE_NAME} (
        project_name    TEXT,
        dataset_name    TEXT,
        table_name      TEXT,
        connection_name TEXT,
        check_name      TEXT,
        status          TEXT,
        additions       TEXT
    );
    """

    sql_statements = [create_table]

    for record in parsed_data:
        project_name, dataset_name, table_name, connection_name, check_name, status, additions = record
        if not INCLUDE_PASSED_CHECKS and status == "PASSED":
            continue
        insert_statement = f"""
        INSERT INTO {SCAN_SUMMARY_TABLE_NAME} (
            project_name,
            dataset_name,
            table_name, 
            connection_name, 
            check_name, 
            status, 
            additions
        ) VALUES (
            '{project_name}',
            '{dataset_name}',
            '{table_name}', 
            '{connection_name}', 
            '{check_name}', 
            '{status}', 
            '{additions}');"""
        sql_statements.append(insert_statement)

    return sql_statements


def gather_yaml_files(directory):
    """Gather all .yml files from a given directory."""
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(directory)
            for name in files if name.endswith(('.yml', '.yaml'))]


def setup_scan():
    """Setup and execute a soda scan."""
    scan = Scan()
    scan.set_scan_definition_name(SCAN_DEFINITION_NAME)
    scan.set_data_source_name(DATA_SOURCE_NAME)
    scan.add_configuration_yaml_file(file_path=CONFIGURATION_YAML)
    for yaml_file in gather_yaml_files(TABLES_DIR):
        scan.add_sodacl_yaml_file(yaml_file)
    scan.set_verbose(LOGS_VERBOSE)
    scan.execute()
    return scan.get_logs_text()


def start_checks():
    os.chdir('/opt/airflow/soda_checks/')
    logs = setup_scan()
    parsed_data = parse_checks(logs)
    sql_statements = generate_sql_inserts(parsed_data)
    execution_results = execute_sql_statements(sql_statements)

    for result in execution_results:
        if result["status"] == "SUCCESS":
            print(f"Executed: {result['statement'][:100]}... SUCCESS")
        else:
            print(f"Failed: {result['statement'][:100]}... {result['status']}")
