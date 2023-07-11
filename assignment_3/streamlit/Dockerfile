FROM python:3.9.13
# Pull the base docker image of python with tag 3.10.6-slim

RUN pip install --upgrade pip
# Upgrade pip package 

WORKDIR /app
# Change the working dir inside the container - cd /app

COPY main.py /app/
# Copy main.py from local streamlit directory to /app directory

COPY pages /app/pages/
# Copy pages directory from local streamlit directory to /app/pages directory

WORKDIR /gen-cv
# Change the working dir inside the container - cd /gen-cv

COPY gen-cv /gen-cv/
# Copy gen-cv directory from local gen-cv directory to /gen-cv directory

RUN pip install -r requirements.txt
# Install the dependencies from requirements.txt

WORKDIR /app
# Change the working dir back to /app - cd /app

EXPOSE 8090

CMD ["streamlit", "run", "main.py", "--server.port", "8090"]
