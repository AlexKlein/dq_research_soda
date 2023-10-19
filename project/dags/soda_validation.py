import sys
import importlib.util
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


SODA_ROOT_DIR = '/opt/airflow/soda_checks'
MODULE_PATH = '/opt/airflow/soda_checks/checks.py'
MODULE_NAME = 'checks'

DEFAULT_ARGS = {
    'owner': 'aleksandr.klein',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False
}


def execute_checks():
    """Import and execute the start_app function from custom_expectations.py."""
    sys.path.insert(0, SODA_ROOT_DIR)

    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
    soda_checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(soda_checks)

    soda_checks.start_checks()


dag_config = {
    'dag_id': 'soda_validation',
    'default_args': DEFAULT_ARGS,
    'description': 'An Airflow DAG to run SODA validations',
    'schedule_interval': '30 8 * * *',
    'max_active_runs': 1,
    'catchup': False,
    'start_date': datetime(2023, 10, 9)
}

with DAG(**dag_config) as dag:

    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')

    soda_checks = PythonOperator(
        task_id='soda_checks',
        python_callable=execute_checks,
        retries=1,
        retry_delay=timedelta(minutes=1)
    )

    start >> soda_checks >> end
