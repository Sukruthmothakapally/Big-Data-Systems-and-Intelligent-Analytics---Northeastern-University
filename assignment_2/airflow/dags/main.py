from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

from google.cloud import storage
# from sqlalchemy import create_engine
import pandas as pd
import os
from google.cloud.sql.connector import Connector
import sqlalchemy

# dag declaration
user_input = {
    "dataset_name": Param(default="20150721_AAPL", type='string', minLength=5, maxLength=255),
}

dag = DAG(
    dag_id="BigData_Pipeline",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["Assignment-2", "damg7245"],
    # default_args=args,
    params=user_input,
)
connector = Connector()

def getconn():
    conn = connector.connect(
        instance_connection_string="virtual-sylph-384316:us-west1:app",
        driver="pg8000",
        user="postgres",
        password="J1ag[@%$#1.@9k^^",
        db="postgres",
    )
    return conn

pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

#1st task
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


#2nd task
def store_data_in_gcs(**kwargs):
    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')

    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    # credential_path="C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\assignment_2\\airflow\\dags\\servicekey.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'


    # Set the project ID and bucket name
    project_id = 'virtual-sylph-384316'
    bucket_name = 'damg7245-assignment-7007'

    # Initialize the Google Cloud Storage client
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    for item in data:
        blob_name = f"{item['company_name']}:{item['date']}:{item['Part']}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(item['plain_text'])
        print(f"Data loaded to Google Cloud Storage: {blob_name}")

#3rd task
def store_metadata_in_cloud_sql(**kwargs):
    bucket_name = 'damg7245-assignment-7007'
    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'
    
    # Store metadata in Cloud SQL
    metadata_df = pd.DataFrame(data)[['date', 'ticker', 'company_name', 'Part']]
    metadata_df['gcs_location'] = f"gs://{bucket_name}/{metadata_df['company_name']}:{metadata_df['date']}:{metadata_df['Part']}"

    metadata_df.to_sql('metadata_table', pool, if_exists='append', index=False)

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
