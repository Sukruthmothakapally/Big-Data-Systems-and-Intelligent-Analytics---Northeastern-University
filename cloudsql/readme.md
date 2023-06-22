## Cloud SQL

Cloud SQL is a fully-managed database service that helps you set up, maintain, manage, and administer your relational databases on Google Cloud Platform.

You can use Cloud SQL with MySQL, PostgreSQL, or SQL Server.

https://cloud.google.com/sql

### Tutorial

1. Create a Postgres Instance following the demo with console
2. Enable the `Cloud SQL Admin API` under IAM
3. Create a Service Account under IAM with the following role and generate a JSON key
    * Cloud SQL Client
4. Place the key under `db_key.json`
5. Create an `.env` file with following variables
    ```text
    GOOGLE_APPLICATION_CREDENTIALS="key_path_and_file_name.json"
    INSTANCE_CONNECTION_NAME="project_name:region:instance_name"
    DB_USER="postgres"                  # default user
    DB_PASS='generated-password'
    DB_NAME="postgres"                  # default database
    ```
6. Create a python venv and install the depencencies
    ```bash
    python -m venv .venv_cloudsql
    source .venv_cloudsql/bin/activate
    pip install -r requirements.txt
    ```
7. Run the script
    ```bash
    python main.py
    ```

### References
* https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/cloud-sql/postgres/sqlalchemy
* https://pypi.org/project/cloud-sql-python-connector/
* https://dbeaver.io/download/
