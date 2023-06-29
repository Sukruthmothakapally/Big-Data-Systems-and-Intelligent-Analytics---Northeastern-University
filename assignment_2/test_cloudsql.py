import os
import pandas as pd
import sqlalchemy
from google.cloud.sql.connector import Connector
from google.cloud import storage
from collections import defaultdict
import requests
import csv

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.\\airflow\\dags\\servicekey.json'

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

def store_metadata_in_cloud_sql():
    # Set the project ID and bucket name
    project_id = 'virtual-sylph-384316'
    bucket_name = 'damg7245-assignment-7007'

    # Initialize the Google Cloud Storage client
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    # Get data from GitHub
    url = "https://raw.githubusercontent.com/Earnings-Call-Dataset/MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction/master/MAEC_Dataset/3M/text.txt"
    page = requests.get(url)
    transcript = page.text

    # Get ticker and company name
    tickers_url = "https://raw.githubusercontent.com/plotly/dash-stock-tickers-demo-app/master/tickers.csv"
    tickers_page = requests.get(tickers_url)
    tickers_data = defaultdict(str)
    for row in csv.DictReader(tickers_page.text.splitlines()):
        tickers_data[row['Symbol']] = row['Company']

    # Store metadata in Cloud SQL
    metadata_df = pd.DataFrame(columns=['date', 'ticker', 'company_name', 'Part', 'gcs_location'])
    
    # List all objects in the bucket
    blobs = list(bucket.list_blobs())

    for blob in blobs:
        # Split the blob name into company_name, date, and Part
        company_name, date, Part = blob.name.split(':')
        
        # Create a new row for the metadata_df DataFrame
        row = {'date': date, 'ticker': '', 'company_name': company_name, 'Part': Part}
        
        # Get the GCS location of the object
        gcs_location = f"gs://{bucket_name}/{blob.name}"
        
        row['gcs_location'] = gcs_location
        
        # Append the new row to the metadata_df DataFrame
        metadata_df = pd.concat([metadata_df, pd.DataFrame([row])], ignore_index=True)

    metadata_df['date'] = pd.to_datetime(metadata_df['date'])
    metadata_df['quarter'] = metadata_df['date'].dt.quarter
    metadata_df['month'] = metadata_df['date'].dt.month

    metadata_df['ticker'] = metadata_df['company_name'].map(lambda x: tickers_data.get(x, ''))
    #create table
    metadata_df.to_sql('metadata_table', pool, if_exists='append', index=False)

    print("Metadata loaded to Cloud SQL")

store_metadata_in_cloud_sql()
