from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

# dag declaration
user_input = {
    "dataset_name": Param(default="20160219_CIR", type='string', minLength=5, maxLength=255),
}

dag = DAG(
    dag_id="demo_data_load",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["labs", "damg7245"],
    # default_args=args,
    params=user_input,
)

def get_data_from_github(**kwargs):
    import requests
    import csv
    from collections import defaultdict
    # Get data from GitHub
    url = f"https://raw.githubusercontent.com/Earnings-Call-Dataset/MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction/master/MAEC_Dataset/{kwargs['params']['dataset_name']}/text.txt"
    page = requests.get(url)
    words = page.text.split()
    first_500_words = ' '.join(words[:250])
    #print(first_500_words)

    # Get ticker and company name
    tickers_url = "https://raw.githubusercontent.com/plotly/dash-stock-tickers-demo-app/master/tickers.csv"
    tickers_page = requests.get(tickers_url)
    tickers_data = defaultdict(str)
    for row in csv.DictReader(tickers_page.text.splitlines()):
        tickers_data[row['Symbol']] = row['Company']
    
    response = {}

    response["date"] = kwargs['params']['dataset_name'].split('_')[0]
    response["plain_text"] = first_500_words
    response["ticker"] = kwargs['params']['dataset_name'].split('_')[-1]
    response["company_name"] = tickers_data[response["ticker"]]

    print(response)

    #redis db to store data of entered company (date, plaintext, ticker, company name) and uses hash of- company name,date columns    
    import os
    import redis
    r = redis.Redis(host=os.getenv("DB_HOST", "redis-stack"),  # Local redis error
                    port=os.getenv("DB_PORT", "6379"),
                    username=os.getenv("DB_USERNAME", ""),
                    password=os.getenv("DB_PASSWORD", ""),
                    decode_responses=True
                    )

    print(r.ping())
    r.hset(f"{kwargs['params']['dataset_name'].split('_')[-1]}:{kwargs['params']['dataset_name'].split('_')[0]}", mapping=response)
    r.close()
    print("Data loaded to redis")

with dag:   

    get_data_from_github = PythonOperator(
        task_id='get_data_from_github',
        python_callable=get_data_from_github,
        provide_context=True,
        dag=dag,
    )

    # Flow
    get_data_from_github