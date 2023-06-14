# Assignment requirement

Intelligence Co is tracking advances in Large language models and is interested in trying out
a pilot project that involves building a contextual search application that leverages vector
similarity search, traditional filtering and hybrid search features to aid financial researchers
search through earnings call transcripts. They envision an application wherein they can
periodically upload text datasets and have investment analysts being able to filter by
company and year and have investment analysts being able to search through earnings call
transcripts to aid research.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisite

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Redis](https://redis.io/download)
- [Streamlit](./streamlit/)
- [Airflow](./airflow/)
- [FastAPI](./fastapi/)

### Installation

1. Install Docker Desktop by following the instructions [here](https://www.docker.com/products/docker-desktop).
2. Install Redis by following the instructions [here](https://redis.io/download). (optional)
3. Install Streamlit by running `pip install streamlit` in your command line.
4. Install Airflow by following the instructions [here](https://airflow.apache.org/docs/apache-airflow/stable/start.html). (optional)
5. Install FastAPI by running `pip install fastapi` and `pip install uvicorn[standard]` in your command line.

### Deployment - Run on local

1. Clone the repository.
2. Create a .env file, Example
    ```bash
    DB_HOST=redis-stack
    DB_PORT=6379
    DB_USERNAME=""
    DB_PASSWORD=""
    ```
3. Navigate to the Assignment_1_real directory and run below command to build and run the project -
   ```bash
    docker-compose -f docker-compose-low.yaml up
   ```
4. Visit
    - Streamlit : http://localhost:30005/
    - RedisInsight : http://localhost:30002/
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
7. Postman endpoints - 
-  GET `/health` for health check
-  POST `/register` to register a user
-  GET `/login` to retrieve the logged in user details with authentication
8. Stop docker containers
    ```bash
    docker-compose -f docker-compose-low.yaml down
    ```
9. Delete docker images
    ```bash
    docker rmi $(docker images -q)
    ```

## Usage

1. Register as a user using Postman by sending a POST request to the FastAPI endpoint with your user details.
2. Log in to the Streamlit frontend using your registered user details.
3. Filter based on company, year, embedding type, part of data and enter your own query to perform vector similarity search.
4. If OPENAI is selected - Enter your own OPENAI API key 
5. The top 5 similar statements will be displayed based on cosine similarity.

## Tech Stack

- **Docker Desktop**: A tool designed to make it easier to create, deploy, and run applications by using containers. In this project, Docker is used to containerize and deploy the application.
  

- **Redis**: An in-memory data structure store used as a database. In this project, Redis is used to store hash keys of the company data with columns - ticker, company name, date, sbert embedding, openai embedding, and part of chunk.


- **Streamlit**: An open-source app framework for creating and sharing custom web apps for machine learning and data science. In this project, Streamlit is used as the frontend for the application where authenticated users can login and perform traditional and hybrid querying on the redis database and finally to display the vector similarity search result.


- **Airflow**: A platform to programmatically author, schedule and monitor workflows. In this project, Airflow is used to extract data from github and to store it in redis using hash keys.


- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. In this project, FastAPI is used as a backend API framework to register a user using HTTP Basic authentication and store the credentials in redis.


- **Postman**: A collaboration platform for API development. In this project, Postman is used for API testing to check the health of FastAPI endpoints and to send POST/GET requests.


- **OpenAI text-embedding-ada-002 model**: A powerful natural language processing model developed by OpenAI. In this project, the OpenAI ADA-embedding model is used to compute embeddings for each chunk of the earnings transcript and add them as a column in the database.


- **SBERT sentence-transformers/all-MiniLM-L6-v2 model**: A sentence embedding model developed by Sentence-BERT. In this project, the SBERT all-llmv6 model is used to compute embeddings for each chunk of the earnings transcript and add them as a column in the database.


- **KNN and cosine similarity**: Techniques used to measure the similarity between vectors. In this project, KNN and cosine similarity are used to perform vector similarity search on the embeddings and retrieve the top 5 statements that are most similar to the user's query.

## Additional Resources

For more detailed information about the project, including snapshots of the working application, please refer to this [codelab](https://codelabs-preview.appspot.com/?file_id=101FZQYWfYfxHDNTEZ28qzYGgoMIOP2VGISQvbXkRs68#0).


## Authors

- Riya
- Sukruth
- Vedant

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.