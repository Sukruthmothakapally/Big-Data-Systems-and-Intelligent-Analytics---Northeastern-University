from diagrams import Cluster, Diagram
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx
from diagrams.onprem.container import Docker
from diagrams.onprem.vcs import Github as GithubLogo

with Diagram("User Recommendation System", show=True):
    github = GithubLogo("GitHub")
    openai = Server("OpenAI Embeddings")
    sbert = Server("SBERT Embeddings")
    auth_user = User("Authenticated User")
    query = Server("User Query")
    top5 = Server("Top 5 Statements")
    docker = Docker("Docker")

    with Cluster("Dockerized Components"):
        airflow = Airflow("Airflow DAGs")
        redis = Redis("Redis")
        fastapi = Nginx("FastAPI Backend")
        streamlit = Server("Streamlit UI")

        github >> airflow >> redis >> openai
        redis >> sbert
        redis >> fastapi >> streamlit >> auth_user >> query >> top5
        [openai, sbert] >> top5

    docker - [airflow, redis, fastapi, streamlit]
