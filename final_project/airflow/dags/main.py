from google.cloud import bigquery
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from airflow.utils.dates import days_ago
import os
import pandas as pd
from sentence_transformers import SentenceTransformer

dag = DAG(
    dag_id="StackAI_Data_Pipeline",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["StackAI", "StackOverFlow Bigquery dataset"],
)

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/servicekey.json'

def Extract_data(**kwargs):

    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Set up query to get the top 3 most repeated tags
    top_tags_query = """
        SELECT tag, COUNT(*) as count
        FROM `bigquery-public-data.stackoverflow.posts_questions`,
        UNNEST(SPLIT(tags, '|')) as tag
        GROUP BY tag
        ORDER BY count DESC
        LIMIT 3
    """

    # Run query to get the top 3 most repeated tags
    top_tags_job = bq_client.query(top_tags_query)
    top_tags_result = top_tags_job.result()
    top_tags = [row[0] for row in top_tags_result]

    # Push the top tags to XCom for use in the next task
    kwargs['ti'].xcom_push(key='top_tags', value=top_tags)

def Transform_and_load_posts_data(**kwargs):
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Pull the top tags from XCom
    top_tags = kwargs['ti'].xcom_pull(key='top_tags', task_ids='Extract_data_from_bigquery')

    # Set up query to insert data into the table
    query = f"""
        INSERT INTO StackAI.posts_cleaned (question_id, question_title, question_body, question_tags, accepted_answer, question_creation_date, accepted_answer_creation_date, accepted_answer_owner_display_name, owner_reputation, accepted_answer_score, accepted_answer_view_count)
        WITH posts_answers AS (
            SELECT
                p1.id AS question_id,
                p1.title AS question_title,
                p1.body AS question_body,
                p1.tags AS question_tags,
                p2.body AS accepted_answer,
                p1.creation_date AS question_creation_date,
                p2.creation_date AS accepted_answer_creation_date,
                u.display_name AS accepted_answer_owner_display_name,
                u.reputation AS owner_reputation,
                p2.score AS accepted_answer_score,
                p2.view_count AS accepted_answer_view_count
            FROM
                `bigquery-public-data.stackoverflow.posts_questions` p1
            LEFT JOIN
                `bigquery-public-data.stackoverflow.posts_answers` p2
            ON
                p1.accepted_answer_id = p2.id
            LEFT JOIN
                `bigquery-public-data.stackoverflow.users` u
            ON
                p2.owner_user_id = u.id
            WHERE
                REGEXP_CONTAINS(p1.tags, r'{top_tags[0]}|{top_tags[1]}|{top_tags[2]}')
        )
        SELECT *
        FROM posts_answers limit 500
    """

    # Run query to insert data into the table
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False

    job = bq_client.query(query, job_config=job_config)
    job.result()

def Transform_and_load_comments_data():
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Set up query to insert data into the table
    query = """
        INSERT INTO StackAI.comments_cleaned (post_id, text, creation_date, score)
        SELECT
            c.post_id,
            c.text,
            c.creation_date,
            c.score
        FROM
            `bigquery-public-data.stackoverflow.comments` c
        JOIN
            `stackai-394819.StackAI.posts_cleaned` p
        ON 
            c.post_id = p.question_id
    """

    # Run query to insert data into the table
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False

    job = bq_client.query(query, job_config=job_config)
    job.result()

def generate_and_store_embeddings(**kwargs):
    
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Set up query to get data from BigQuery table
    query = f"""
        SELECT *
        FROM `{kwargs['table_name']}`
    """

    # Run query and fetch results into pandas DataFrame
    df = bq_client.query(query).to_dataframe()

    # Concatenate relevant columns for embedding, handling NaN values
    relevant_text = df.apply(lambda row: ' '.join(filter(lambda x: pd.notna(x), [row['question_title'], row['question_body'] , row['accepted_answer']])), axis=1)

    # Convert relevant_text to a list
    relevant_text_list = relevant_text.tolist()

    # Load the pre-trained Sentence Transformers model
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    def generate_embeddings(text):
        embeddings = model.encode(text)
        return embeddings

    # Generate embeddings for relevant data
    data_embeddings = generate_embeddings(relevant_text_list)

    # Add new column to DataFrame with embeddings
    df['embeddings'] = data_embeddings.tolist()

    # Update BigQuery table with new column
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        schema=[
            bigquery.SchemaField("embeddings", "STRING"),
        ],
    )

    job = bq_client.load_table_from_dataframe(
        df, kwargs['table_name'], job_config=job_config
    )
    job.result()  # Waits for table load to complete.
    print(f"Embeddings generated and stored in {kwargs['table_name']}.")

def extract_cleaned_dataset(**kwargs):
    
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Set up query to get data from BigQuery table
    query = f"""
        SELECT *
        FROM `{kwargs['table_name']}`
    """

    query2 = f"""
        SELECT *
        FROM `{kwargs['table_name2']}`
    """

    # Run query and fetch results into pandas DataFrame
    df = bq_client.query(query).to_dataframe()

    #save to posts csv
    df.to_csv('../data/cleaned_posts.csv', index=False)

    #Run query and fetch results into pandas DataFrame
    df2 = bq_client.query(query2).to_dataframe()

    #save to comments csv
    df2.to_csv('../data/cleaned_comments.csv', index=False)

with dag:
    Extract_data_task=PythonOperator(
        task_id='Extract_data_from_bigquery',
        python_callable=Extract_data,
        provide_context=True,
        dag=dag,
    )

    Transform_and_load_posts_data_task=PythonOperator(
        task_id='Transform_and_load_data_into_custom_posts_table',
        python_callable=Transform_and_load_posts_data,
        provide_context=True,
        dag=dag,
    )

    Transform_and_load_comments_data_task=PythonOperator(
        task_id='Transform_and_load_data_into_custom_comments_table',
        python_callable=Transform_and_load_comments_data,
        provide_context=True,
        dag=dag,
    )

    generate_and_store_embeddings_task = PythonOperator(
    task_id='generate_and_store_embeddings',
    python_callable=generate_and_store_embeddings,
    op_kwargs={
        'project_id': 'stackai-394819',
        'table_name': 'stackai-394819.StackAI.posts_cleaned'
    },
    dag=dag,
    )

    extract_cleaned_dataset_task = PythonOperator(
    task_id='extract_cleaned_dataset',
    python_callable=extract_cleaned_dataset,
    op_kwargs={
        'project_id': 'stackai-394819',
        'table_name': 'stackai-394819.StackAI.posts_cleaned',
        'table_name2': 'stackai-394819.StackAI.comments_cleaned'
    },
    dag=dag,
)

Extract_data_task >> Transform_and_load_posts_data_task >> Transform_and_load_comments_data_task >> generate_and_store_embeddings_task >> extract_cleaned_dataset_task

