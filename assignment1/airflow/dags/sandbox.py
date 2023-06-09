from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
# from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta

dag = DAG(
    dag_id="sandbox",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["labs", "damg7245"],
    # params=user_input,
)

with dag:
    hello_world = BashOperator(
        task_id="hello_world",
        bash_command='echo "Hello from airflow"'
    )

    bye_world = BashOperator(
        task_id="bye_world",
        bash_command='echo "Bye from airflow"'
    )

    next_world = BashOperator(
        task_id="next_world",
        bash_command='echo "next from airflow"'
    )

    # Flow
    hello_world >> bye_world >> next_world