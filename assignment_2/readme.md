# Assignment requirement

Intelligence Co has hired you as a software engineer. You are a fintech that intends
to use data and analytics to help analysts make investment recommendations. They
track many stocks and intend to build an on-the-fly document summarization engine
for earnings call transcripts.
The specification of the project is as follows:
Intelligence Co reviewed the solution using Redis (Assignment 1) and now thinks they
need to evaluate other products too. They intend to try Cloud SQL with Postgres SQL
and Pine cone for the following use case. The company expects transcripts to be in the
format and the naming convention used in.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisite

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Streamlit](./streamlit/)
- [Airflow](./airflow/)
- [FastAPI](./fastapi/)

### Installation

1. Install Docker Desktop by following the instructions [here](https://www.docker.com/products/docker-desktop).
2. Install Streamlit by running `pip install streamlit` in your command line.
3. Install Airflow by following the instructions [here](https://airflow.apache.org/docs/apache-airflow/stable/start.html). (optional)
4. Install FastAPI by running `pip install fastapi` and `pip install uvicorn[standard]` in your command line.

### Deployment - Run on local

1. Clone the repository.
2. Create a .env file
3. Navigate to the Assignment_1_real directory and run below command to build and run the project -
   ```bash
    docker compose up
   ```
4. Visit
    - Streamlit : http://localhost:30005/
    - airflow : http://localhost:8080/
    - fastapi : http://localhost:30004/
5. Register a user using fastapi and postman POST method - http://localhost:30004/register?username=your_username&password=your_password
6. Trigger a dag with custom config (company name) -
   Postman POST method - http://localhost:8080/api/v1/dags/data_load/dagRuns - Sample body config given below -
   ```bash
   {
  "conf": {
    "dataset_name": "20150226_ACIW"
  },
  "dag_run_id": "string17", 
  "logical_date": "2023-06-11T17:06:08.694Z",
  "note": "string"
    }```
1. Postman endpoints - 
-  GET `/health` for health check
-  POST `/register` to register a user
-  GET `/login` to retrieve the logged in user details with authentication
1. Stop docker containers
    ```bash
    docker compose down
    ```
2. Delete docker images
    ```bash
    docker rmi $(docker images -q)
    ```

## Usage

1. Register as a user using Postman by sending a POST request to the FastAPI endpoint with your user details.
2. Log in to the Streamlit frontend using your registered user details.
3. Filter based on company and year. OpenAI Summary of the earnings statement for that company and year would be displayed.
4. User will have the option to view the complete transcript and ask questions regarding it.
5. Once the user queries an input, relevant answer will be displayed using OpenAI model - text-embedding-ada-002" semantic search.
6. Users can also obtain LangChain summary and Generative question and answering for the given transcript.

## Tech Stack

- **Docker Desktop**: A tool designed to make it easier to create, deploy, and run applications by using containers. In this project, Docker is used to containerize and deploy the application.


- **Streamlit**: An open-source app framework for creating and sharing custom web apps for machine learning and data science. In this project, Streamlit is used as the frontend for the application where authenticated users can login and perform hybrid filtering and querying on the companies to obtain the earnings statement summary and answers related to it using LangChain and OpenAI models.


- **Airflow**: A platform to programmatically author, schedule and monitor workflows. In this project, Airflow is used to extract data from github and to store it in redis using hash keys.


- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. In this project, FastAPI is used as a backend API framework to register a user using HTTP Basic authentication and store the credentials in redis.


- **Postman**: A collaboration platform for API development. In this project, Postman is used for API testing to check the health of FastAPI endpoints and to send POST/GET requests.


- **OpenAI text-embedding-ada-002 model**: A powerful natural language processing model developed by OpenAI. In this project, the OpenAI ADA-embedding model is used to compute embeddings for each chunk of the earnings transcript and store the them in pinecone.


- **Pinecone**: A vector database service that enables fast similarity search on large-scale vector data. In this project, Pinecone is used to store OpenAI embeddings for each chunk of the earnings transcript.


- **Cloud SQL**: A fully-managed database service that makes it easy to set up, maintain, manage, and administer your relational databases on Google Cloud Platform. In this project, Cloud SQL is used to store metadata about companies.


- **Google Cloud Storage**: An object storage service that allows you to store and access your data on Google’s infrastructure. In this project, Google Cloud Storage is used to store data from GitHub in a bucket.


- **Langchain**: A language model that can generate human-like text. In this project, Langchain is used as an LLM model for summarization and generative Q&A.


## Additional Resources

For more detailed information about the project, including snapshots of the working application, please refer to this [codelab](https://codelabs-preview.appspot.com/?file_id=101FZQYWfYfxHDNTEZ28qzYGgoMIOP2VGISQvbXkRs68#0).


## Authors

- Riya
- Sukruth
- Vedant

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.