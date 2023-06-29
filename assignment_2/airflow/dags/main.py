from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

from google.cloud import storage
# from sqlalchemy import create_engine
#import pandas
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

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'

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

pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn).connect()

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

    response = {}

    response["date"] = kwargs['params']['dataset_name'].split('_')[0]
    response["plain_text"] = transcript
    response["ticker"] = kwargs['params']['dataset_name'].split('_')[-1]
    response["company_name"] = tickers_data.get(response["ticker"], "Company not found")

    ti.xcom_push(key='data', value=response)
    print(f"response: {response}, type: {type(response)}")


#2nd task
def store_data_in_gcs(**kwargs):
    from google.cloud import storage
    import os

    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')

    # Set the environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'

    # Set the project ID and bucket name
    project_id = 'virtual-sylph-384316'
    bucket_name = 'damg7245-assignment-7007'

    # Initialize the Google Cloud Storage client
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    blob_name = f"{data['company_name']}:{data['date'][:4]}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data['plain_text'])
    print(f"Data loaded to Google Cloud Storage: {blob_name}")

    # Push the blob_name variable to XCom
    kwargs['ti'].xcom_push(key='blob_name', value=blob_name)



#3rd task
def store_metadata_in_cloud_sql(**kwargs):
    import pandas as pd
    from google.cloud import storage

    # Set the bucket name
    bucket_name = 'damg7245-assignment-7007'

    print("Getting data from XCom...")  # to see if the task is getting stuck here
    # Get data from XCom
    data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data_from_github_task')
    print(f"date: {data['date']}")

    print("Storing metadata in Cloud SQL...")  # to see if the task is getting stuck here
    # Store metadata in Cloud SQL
    metadata_df = pd.DataFrame([data])[['date', 'ticker', 'company_name']]
    metadata_df['date'] = pd.to_datetime(metadata_df['date'], format="%Y%m%d")
    metadata_df['quarter'] = metadata_df['date'].dt.quarter
    metadata_df['month'] = metadata_df['date'].dt.month

    # Get the public URL of the GCS object
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob_name = kwargs['ti'].xcom_pull(key='blob_name', task_ids='store_data_in_gcs_task')
    blob = bucket.blob(blob_name)
    public_url = blob.public_url
    metadata_df['public_url'] = public_url

    print("Connecting to Cloud SQL...")  # to see if the task is able to connect to your Cloud SQL instance
    try:
        print(f"pool: {pool}")  # to see if the pool variable is defined correctly
        metadata_df.to_sql('Companies_metadata', pool, if_exists='append', index=False)
        print("Metadata loaded to Cloud SQL")
    except Exception as e:
        print(f"Error while loading data to Cloud SQL: {e}")  # to see if there are any errors while loading data to Cloud SQL


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
