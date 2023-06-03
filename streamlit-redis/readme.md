# Streamlit 

Streamlit is an open-source app framework for Machine Learning and Data Science teams to create beautiful web apps in minutes.

## Steps

### Run on Local

1. Open Docker Desktop
2. Start docker containers
    ```docker compose -f dockerfile up -d
    ```
3. Visit
    - Streamlit : http://localhost:8090/
    - RedisInsight : http://localhost:8001/
4. Stop docker containers
    ```docker compose -f dockerfile down
    ```

### Run on Cloud
1. Setup a managed Redis Database
    - https://redis.com/redis-enterprise-cloud/pricing/
    - https://devcenter.heroku.com/categories/heroku-redis
    
    Refer the terraform [Readme](./terraform/README.md) on creating resources.

2. Update the [.env_cloud](./.env_cloud) file, Example
    ```bash
    DB_HOST=redis-service.com
    DB_PORT=1234
    DB_USERNAME=default
    DB_PASSWORD=abc123xyz
    ```

3. Start docker containers
    ```bash
    make cloud-up
    ```

4. Visit
    - Streamlit : http://localhost:8095/
  
5. Stop docker containers
    ```bash
    make cloud-down
    ```
    
6. Deploy on Streamlit Cloud

