FROM apache/airflow:2.6.1
USER root
RUN apt-get update && apt-get -y upgrade
# RUN apt-get install -y redis-tools
RUN apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
USER airflow
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt

# Install Terraform
USER root
RUN apt-get update && apt-get install -y wget unzip
RUN wget https://releases.hashicorp.com/terraform/1.3.8/terraform_1.3.8_linux_amd64.zip \
    && unzip terraform_1.3.8_linux_amd64.zip \
    && mv terraform /usr/local/bin/

# # Copy JSON credentials file into container
# COPY stackai-394819-86a97a8439b6.json /etc/gcp/credentials.json

# Copy Terraform configuration into container
COPY pipeline/terraform/main.tf /etc/terraform/main.tf