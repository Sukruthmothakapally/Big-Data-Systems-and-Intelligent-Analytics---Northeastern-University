from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.workflow import Airflow
from diagrams.gcp.storage import Storage
from diagrams.gcp.database import SQL
from diagrams.onprem.network import Nginx
from diagrams.onprem.container import Docker
from diagrams.onprem.vcs import Github as GithubLogo

with Diagram("User Recommendation System", show=True):
    github = GithubLogo("GitHub")
    openai = Server("OpenAI Embeddings")
    query = Server("User Query")
    result = Server("Summary and Generative QA")
    docker = Docker("Docker")
    langchain = Server("Langchain")
    pinecone = Server("Pinecone")

    with Cluster("Dockerized Components"):
        airflow = Airflow("Airflow DAGs")
        streamlit = Server("Streamlit UI")

        with Cluster("Google Cloud"):
            gcs = Storage("Google Cloud Storage")
            cloudsql = SQL("Cloud SQL")

            Edge(github, airflow, label="Get data from GitHub")
            Edge(airflow, gcs, label="Store data in GCS")
            Edge(gcs, cloudsql, label="Store metadata in Cloud SQL")

            github >> airflow >> gcs >> cloudsql >> streamlit >> query >> [openai, langchain] >> pinecone >> result

    docker - [airflow, streamlit]
