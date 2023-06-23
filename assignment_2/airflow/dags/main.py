from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

from google.cloud import storage
from sqlalchemy import create_engine
import pandas as pd
import os

# dag declaration
user_input = {
    "dataset_name": Param(default="20150721_AAPL", type='string', minLength=5, maxLength=255),
}

dag = DAG(
    dag_id="Data_Pipeline",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["Assignment-2", "damg7245"],
    # default_args=args,
    params=user_input,
)

def get_data_from_github(**kwargs):
    import requests
    import csv
    from collections import defaultdict

    ti = kwargs['ti']

    # Get data from GitHub
    url = f"https://raw.githubusercontent.com/Earnings-Call-Dataset/MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction/master/MAEC_Dataset/{kwargs['params']['dataset_name']}/text.txt"
    page = requests.get(url)
    transcript = page.text

    # Get ticker and company name
    tickers_url = "https://raw.githubusercontent.com/plotly/dash-stock-tickers-demo-app/master/tickers.csv"
    tickers_page = requests.get(tickers_url)
    tickers_data = defaultdict(str)
    for row in csv.DictReader(tickers_page.text.splitlines()):
        tickers_data[row['Symbol']] = row['Company']

    words = transcript.split()
    chunks = [words[i:i + 500] for i in range(0, len(words), 500)]

    response = []

    for i, chunk in enumerate(chunks):
        response_chunk = {}

        response_chunk["date"] = kwargs['params']['dataset_name'].split('_')[0]
        response_chunk["plain_text"] = ' '.join(chunk)
        response_chunk["ticker"] = kwargs['params']['dataset_name'].split('_')[-1]
        response_chunk["company_name"] = tickers_data.get(response_chunk["ticker"], "Company not found")
        response_chunk["Part"] = i + 1

        response.append(response_chunk)

    ti.xcom_push(key='data', value=response)

def store_data_in_gcs(**kwargs):
    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')

    # Store data in Google Cloud Storage
    bucket_name = 'damg7245-assignment-7007'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for item in data:
        blob_name = f"{item['company_name']}:{item['date']}:{item['Part']}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(item['plain_text'])
        print(f"Data loaded to Google Cloud Storage: {blob_name}")


def store_metadata_in_cloud_sql(**kwargs):
    bucket_name = 'damg7245-assignment-7007'
    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')

    # Store metadata in Cloud SQL
    db_user = 'postgres'
    db_pass = 'J1ag[@%$#1.@9k^^'
    db_name = 'postgres'
    cloud_sql_connection_name = 'virtual-sylph-384316:us-west1:app'

    db_socket_dir = '/cloudsql'
    driver_name = 'postgres+pg8000'
    query_string = dict({"unix_sock": "{}/{}/.s.PGSQL.5432".format(db_socket_dir, cloud_sql_connection_name)})

    db_engine = create_engine(f"{driver_name}://{db_user}:{db_pass}@/{db_name}", connect_args=query_string)

    metadata_df = pd.DataFrame(data)[['date', 'ticker', 'company_name', 'Part']]
    metadata_df['gcs_location'] = f"gs://{bucket_name}/{metadata_df['company_name']}:{metadata_df['date']}:{metadata_df['Part']}"

    metadata_df.to_sql('metadata_table', db_engine, if_exists='append', index=False)

    print("Metadata loaded to Cloud SQL")


with dag:  

    get_data_from_github_task=PythonOperator(
    task_id='get_data_from_github_task',
    python_callable=get_data_from_github,
    provide_context=True,
    dag=dag,
    )

    store_data_in_gcs_task=PythonOperator(
    task_id='store_data_in_gcs_task',
    python_callable=store_data_in_gcs,
    provide_context=True,
    dag=dag,
    )

    store_metadata_in_cloud_sql_task=PythonOperator(
    task_id='store_metadata_in_cloud_sql_task',
    python_callable=store_metadata_in_cloud_sql,
    provide_context=True,
    dag=dag,
    )

# Flow
get_data_from_github_task>>store_data_in_gcs_task>>store_metadata_in_cloud_sql_task
