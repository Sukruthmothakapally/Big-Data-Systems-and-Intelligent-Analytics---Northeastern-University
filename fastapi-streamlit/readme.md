## FastAPI with Streamlit

* __FastAPI__ 

    2 endpoints
1. `api/v1/health` for health check
2. `api/v1/tokenize` for tokenizing sentences


* __Streamlit__

    Define the environment variable `API_URL` as the URL for the fastapi service

Refer the [notebook](./Authentication.ipynb) to implement Authentication

### Steps:
1. To run the containers with building image
    ```bash
    make build-up
    ```
    OR
    To run the container without building image if the image already exists
    ```bash
    #make up
    ```
2. Visit the individual services
   * FastAPI - http://localhost:8095/docs
   * Streamlit - http://localhost:8090/
3. To stop the containers
    ```bash
    #make down
    ```