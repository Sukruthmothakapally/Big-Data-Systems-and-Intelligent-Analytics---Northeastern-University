from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.container import Docker
from diagrams.onprem.iac import Terraform
from diagrams.gcp.compute import ComputeEngine, GCE 
from diagrams.programming.framework import Fastapi, FastAPI
from diagrams.saas.analytics import Snowflake
from diagrams.programming.language import Python
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.compute import Server

with Diagram("Implemented Architecture for STACKAI", show=True):

    streamlit = Custom("Streamlit", "./logos/streamlit.jpg")
    docker = Docker("Docker")
    #github actions
    github = Custom("Github Actions", "./logos/githubactions.jpg")
    terraform = Terraform("Terraform")
    gcp = Custom("App hosted on GCP","./logos/gcp.png") 
    fastapi = FastAPI("FAST API Backend")
    bigquery = Custom("GCP Bigquery Data Source","./logos/gcpbigquery.png")
    cloudsql = Custom("CloudSQL","./logos/cloudsql.png")
    airflow = Airflow("Airflow DAGs")
    

    with Cluster("Airflow"):
        extract = Custom("Extract Relevant Data", "./logos/extract.png")
        clean = Custom("Transform Data", "./logos/datatransform.jpg")
        load = Custom("Load Data into Bigquery", "./logos/gcpbigquery.png")
        embeddings = Custom("Generate embeddings", "./logos/sbert.png")
        grtexp = Custom("Great Expectations Analysis","./logos/greatexpectations.jpg")

        airflow >> extract >> clean >> load >> embeddings >> grtexp

    with Cluster("Streamlit"):
        signup = Custom("user sign up", "./logos/usersignup.jpg")
        signin = Custom("logged-in user", "./logos/user.jpg")
        category = Custom("Select a category", "./logos/userselection.jpg")
        #user input
        user_input = Custom("Ask a question", "./logos/userinput.jpg")

        sbert_logo = Custom("Sbert Similarity Search", "./logos/sbert.png")

        with Cluster("OpenAI"):
            openai_summary = Custom("Summarization", "./logos/openai.jpg")
            openai_genqa = Custom("Generative Q/A", "./logos/openai.jpg")
            openai_craft = Custom("Craft a Question", "./logos/openai.jpg")
            openai_summary >> openai_genqa >> openai_craft

        streamlit >> signup >> signin >> category >> user_input >> sbert_logo >> openai_summary

    

    with Cluster("Streamlit Other Features"):
        stats = Custom("Stackoverflow stats", "./logos/stackoverflow.jpg")
        dashboard = Custom("User Dashboard", "./logos/userdashboard.jpg")

        streamlit >> stats >> dashboard



    with Cluster("Docker"):
        dockerize_airflow = Airflow("Airflow")
        dockerize_fastapi = FastAPI("FastAPI")
        dockerize_streamlit = Custom("Streamlit", "./logos/streamlit.jpg")

        docker >> dockerize_airflow >> dockerize_fastapi >> dockerize_streamlit

    streamlit<<Edge(label="Dockerise the whole app")<<docker>>terraform>>Edge(label="Create GCP Infrastructure")>>gcp

    with Cluster("Pytest"):
        push_project = Custom("Unit Testing", "./logos/unittesting.png")
        pytest_unit_test = Custom("API Testing", "./logos/apitesting.png")

        github >> push_project >> pytest_unit_test

    gcp << Edge(label="Continuous Integration") >> github

    streamlit<<Edge(label="Used to make API calls")>>fastapi>>Edge(label="Access User Database")>>cloudsql
    bigquery<<Edge(label="Data Source & Big Data Storage")>>Edge(label="Data Pipeline")>>airflow
