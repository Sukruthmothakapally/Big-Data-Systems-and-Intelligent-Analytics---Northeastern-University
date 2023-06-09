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
    url = f"https://raw.githubusercontent.com/Earnings-Call-Dataset/MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction/master/MAEC_Dataset/{kwargs['params']['dataset_name']}/text.txt"
    page = requests.get(url)
    words = page.text.split()
    first_500_words = ' '.join(words[:250])
    #print(first_500_words)

    #hugging face embedding service
    import numpy as np
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(first_500_words)
    response = {}
    response["date"] = kwargs['params']['dataset_name'].split('_')[0]
    response["plain_text"] = first_500_words
    vector = np.array(embeddings).astype(np.float32).tobytes()
    response["embeddings"] = vector
    print(response)

    #redis db to store data of entered company (date, plaintext, embeddings) and uses hash of- company name,date columns    
    import os
    import redis
    r = redis.Redis(host=os.getenv("DB_HOST", "redis-stack"),  # Local redis error
                    port=os.getenv("DB_PORT", "6379"),
                    username=os.getenv("DB_USERNAME", ""),
                    password=os.getenv("DB_PASSWORD", ""),
                    decode_responses=True
                    )
    # r = redis.Redis.from_url("redis://:@redis-user-client:6379/0")
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