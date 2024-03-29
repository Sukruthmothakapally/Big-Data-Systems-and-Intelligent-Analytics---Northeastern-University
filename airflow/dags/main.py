from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Set default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'StackAI_Data_Pipeline',
    default_args=default_args,
    description='DAG to GCP infrastructure with Terraform and Extraction, Transformation, and loading of data in BigQuery',
    schedule_interval=timedelta(days=1),
)

# Define the Terraform task
terraform_task = BashOperator(
    task_id='run_terraform',
    bash_command='cd /etc/terraform && terraform apply -auto-approve',
    dag=dag,
)

# Define the Python ETL task
def python_etl():
    from google.cloud import bigquery

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

python_etl_task = PythonOperator(
    task_id='run_python_etl',
    python_callable=python_etl,
    dag=dag,
)

# Set task dependencies
terraform_task >> python_etl_task
