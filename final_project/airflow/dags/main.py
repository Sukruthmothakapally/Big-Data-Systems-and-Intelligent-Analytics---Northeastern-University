from google.cloud import bigquery
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta
from airflow.utils.dates import days_ago
import os
import pandas as pd
import great_expectations as ge
import logging
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
        SELECT tags, COUNT(*) as count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        GROUP BY tags
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
        INSERT INTO StackAI.posts_cleaned (question_id, question_title, question_body, question_tags, question_score, question_view_count, answer_count, comment_count, question_creation_date, accepted_answer, accepted_answer_creation_date, accepted_answer_owner_display_name, owner_reputation, owner_badge, accepted_answer_score, accepted_answer_view_count)
        WITH posts_answers AS (
            SELECT
                p1.id AS question_id,
                COALESCE(p1.title, 'N/A') AS question_title,
                COALESCE(p1.body, 'N/A') AS question_body,
                COALESCE(p1.tags, 'N/A') AS question_tags,
                COALESCE(p1.score, 0) AS question_score,
                COALESCE(SAFE_CAST(p1.view_count AS INT64), 0) AS question_view_count,
                COALESCE(p1.answer_count, 0) AS answer_count,
                COALESCE(p1.comment_count, 0) AS comment_count,
                COALESCE(FORMAT_DATE('%Y-%m-%d', DATE(p1.creation_date)), 'N/A') AS question_creation_date,
                COALESCE(p2.body, 'N/A') AS accepted_answer,
                COALESCE(FORMAT_DATE('%Y-%m-%d', DATE(p2.creation_date)), 'N/A') AS accepted_answer_creation_date,
                COALESCE(u.display_name, 'N/A') AS accepted_answer_owner_display_name,
                COALESCE(u.reputation, 0) AS owner_reputation,
                COALESCE(b.name, 'N/A') AS owner_badge,
                COALESCE(p2.score, 0) AS accepted_answer_score,
                COALESCE(SAFE_CAST(p2.view_count AS INT64), 0) AS accepted_answer_view_count
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
            LEFT JOIN
                `bigquery-public-data.stackoverflow.badges` b
            ON
                p2.id = b.id
            WHERE
                p1.tags IN ('{top_tags[0]}', '{top_tags[1]}', '{top_tags[2]}')
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
            COALESCE(c.text, 'N/A') AS text,
            COALESCE(FORMAT_DATE('%Y-%m-%d', DATE(c.creation_date)), 'N/A') AS creation_date,
            COALESCE(c.score, 0) AS score
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

    # Set up query
    query = f"""
        SELECT *
        FROM `{kwargs['table_name']}`
    """

    # Run query and fetch results into pandas DataFrame
    df = bq_client.query(query).to_dataframe()

    # Concatenate relevant columns for embedding, handling 'N/A' values
    relevant_text = df.apply(lambda row: ' '.join(filter(lambda x: x != 'N/A', [row['question_title'], row['question_body'] , row['accepted_answer']])), axis=1)

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
            bigquery.SchemaField("embeddings", "FLOAT64", mode="REPEATED"),
        ],
    )

    job = bq_client.load_table_from_dataframe(
        df, kwargs['table_name'], job_config=job_config
    )
    job.result()  # Waits for table load to complete.
    print(f"Embeddings generated and stored in {kwargs['table_name']}.")

def great_expectations_analysis(**kwargs):
    # Set up BigQuery client with explicit project ID
    bq_client = bigquery.Client(project='stackai-394819')

    # Fetch the data from BigQuery into a DataFrame
    query = """
        SELECT *
        FROM `stackai-394819.StackAI.posts_cleaned`
    """
    df = bq_client.query(query).to_dataframe()

    # Create a Great Expectations Batch from the DataFrame
    batch = ge.dataset.PandasDataset(df)  # Correct class name

    # Define your expectations
    batch.expect_column_values_to_not_be_null('question_id')

    # Validate the Batch and get the results
    results = batch.validate()

    # Log the validation results
    logging.info("Great Expectations validation results:")
    logging.info(results)

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

#Task to run Great Expectations
    ge_task = PythonOperator(
        task_id='run_great_expectations',
        python_callable=great_expectations_analysis,
        provide_context=True,
        dag=dag,
    )

Extract_data_task >> Transform_and_load_posts_data_task >> Transform_and_load_comments_data_task >> generate_and_store_embeddings_task >> ge_task

