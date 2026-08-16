from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "sudharsan",
    "depends_on_past": False,
}

with DAG(
    dag_id="warehouse_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    catchup=False,
    schedule=None,
    tags=["de-poc"],
) as dag:

    ingest = BashOperator(
        task_id="bronze_ingestion",
        bash_command="cd /opt/airflow/scripts && python ingestion.py",
    )

    ingest_api = BashOperator(
        task_id="synthetic_api_ingestion",
        bash_command="cd /opt/airflow/scripts && python ingestion/load_synthetic_api.py",
    )

    silver = BashOperator(
        task_id="silver_transformations",
        bash_command="cd /opt/airflow/scripts && python silver_transformations.py",
    )

    scd = BashOperator(
        task_id="scd_processing",
        bash_command="cd /opt/airflow/scripts && python scd.py --type 2",
    )

    star_schema = BashOperator(
        task_id="star_schema_transformations",
        bash_command="cd /opt/airflow/scripts && python star_schema_transformations.py",
    )

    gold = BashOperator(
        task_id="gold_transformations",
        bash_command="cd /opt/airflow/scripts && python gold_transformations.py",
    )

    validation = BashOperator(
        task_id="validation",
        bash_command="cd /opt/airflow/scripts && python validation.py",
    )

    gx_validation = BashOperator(
        task_id="great_expectations_validation",
        bash_command="cd /opt/airflow/scripts && python gx_validation.py",
    )

    [ingest, ingest_api] >> silver >> scd >> star_schema >> gold >> validation >> gx_validation
