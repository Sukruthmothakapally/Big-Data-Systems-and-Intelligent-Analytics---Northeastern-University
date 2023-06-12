from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

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
    tags=["Assignment-1", "damg7245"],
    # default_args=args,
    params=user_input,
)

def get_data_from_github(**kwargs):
    import requests
    import csv
    from collections import defaultdict
    import numpy as np

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

    # SBert Embeddings
    from sentence_transformers import SentenceTransformer
    sbert_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    import openai
    openai.api_key = "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"

    def get_openai_embeddings(prompt):
        response = openai.Embedding.create(
            input=prompt,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

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

        # Encode chunk with SBert model
        sbert_embeddings = sbert_model.encode([' '.join(chunk)], convert_to_tensor=True).numpy()
        response_chunk["sbert_embeddings"] = sbert_embeddings.tostring()

        # Encode chunk with OpenAI model
        openai_embeddings = get_openai_embeddings(' '.join(chunk))
        openai_embeddings = np.array(openai_embeddings)
        response_chunk["openai_embeddings"] = openai_embeddings.tostring()

        response.append(response_chunk)

    # Store data in Redis
    import os
    import redis

    r = redis.Redis(
        host=os.getenv("DB_HOST", "redis-stack"),
        port=os.getenv("DB_PORT", "6379"),
        username=os.getenv("DB_USERNAME", ""),
        password=os.getenv("DB_PASSWORD", ""),
        decode_responses=True
    )

    if r.ping():
        for item in response:
            hash_key = f"{item['company_name']}:{item['date']}:{item['Part']}"
            #item["sbert_embeddings"] = item["sbert_embeddings"].tostring()
            #item["openai_embeddings"] = item["openai_embeddings"].tostring()
            r.hset(hash_key, mapping=item)

        r.close()
        print("Data loaded to Redis")
    else:
        print("Failed to connect to Redis")

    print(response)

with dag:  

    get_data_from_github = PythonOperator(
        task_id='github_redis',
        python_callable=get_data_from_github,
        provide_context=True,
        dag=dag,
    )

    # Flow
    get_data_from_github