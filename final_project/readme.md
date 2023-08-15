final project

# gcp git clone updates -

- add .env file
- add service key in dags folder
- removed logs volume in docker compose
- sudo chown -R sukruth_mothakapally:sukruth_mothakapally final_project/

# STACKAI 🤖🧠

## Please find the app hosted on GCP (for a limited time only) - 

User Inteferface : [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](http://34.102.9.117:30005/)

Backend : [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](http://34.148.167.159:8050/docs)

Data Pipeline : [![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-007A88?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)](http://34.138.127.169:8080/)

Documentation : [![codelabs](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=1blarGD_LQ5o5aGcJWiKKbhDBissQSL9qfs28dx5HyFk#11)

App Demo : [![Youtube](https://img.shields.io/badge/Demo_Link-808080?style=for-the-badge&logo=YouTube&logoColor=white)](https://youtu.be/DnmAYNL0kcI)







## Abstract :memo: 

In response to a noticeable decline in traffic on Stack Overflow – once a thriving developer community platform – due to the rise of OpenAI's ChatGPT, an application named "StackAI" has been developed. This strategic endeavor aims to restore Stack Overflow's status as a preferred destination for developers seeking coding solutions. By integrating advanced AI features, StackAI strives to rejuvenate community engagement while preserving its core values.
StackAI's key features include a Topic Relevance Search, enabling users to swiftly navigate through relevant topics according to the user input, Stack Overflow's extensive knowledge base, and Topic Summarization, which delivers concise insights for efficient understanding. Moreover, AI-Generated Answers supplement the existing dataset, addressing users' unique queries and maintaining the platform's relevancy.
The project encompasses meticulous data collection, preprocessing, and validation. It establishes a robust data pipeline, deploys advanced models like SentenceTransformer and langchain chains summarize, and uses FASTAPI for a responsive backend. A user-friendly interface is developed using Streamlit, while Terraform automates the provisioning of crucial GCP resources for Infrastructure as a Service. Comprehensive testing, continuous integration, and deployment using GitHub Actions ensure a seamless user experience.
Ultimately, StackAI aims to reinvigorate Stack Overflow's community spirit and contribute to a dynamic ecosystem of knowledge exchange by harnessing AI-powered features, enhancing user interactions, and adapting to evolving developer needs.
management.

## Project Goals :dart:


**Enhance User Engagement:** The primary aim of the project is to revitalize the Stack Overflow community by leveraging advanced AI features through "StackAI." This initiative seeks to counter the decline in traffic and engage developers by providing comprehensive AI-driven solutions to their programming inquiries, fostering a renewed sense of interaction and knowledge sharing.

**Adapt to Changing Landscape:** With the rising popularity of OpenAI's ChatGPT, the project aims to adapt to the changing developer landscape. By incorporating AI-generated answers and other AI-driven features, StackAI aims to stay relevant and continue being a preferred destination for developers seeking coding solutions.

**Facilitate Efficient Information Retrieval:** The project aims to provide users with an enhanced experience by enabling them to quickly navigate through the vast knowledge base of Stack Overflow. The Topic Relevance Search feature utilizes advanced NLP models to identify and present users with the most relevant topics associated with their questions.

**Improve User Comprehension:** To cater to diverse user needs, the Topic Summarization feature condenses complex programming concepts into concise summaries. This goal enhances user comprehension and facilitates quicker understanding of intricate topics, thereby enriching the learning experience.

**Provide Reliable and Automated Data Processing:** The project focuses on ensuring data quality through robust data validation and preprocessing, implemented via tools like Great Expectations and Airflow. By automating data pipelines and deployment using CI/CD practices, the project guarantees that users interact with accurate, relevant, and up-to-date information.

By achieving these goals, "StackAI" seeks to reinvent Stack Overflow as a vibrant hub for developers, fostering community engagement, adapting to the evolving technology landscape, and delivering valuable, AI-powered insights to its users.





## Data Source :flashlight:

The data source for this project is the Google Bigquery Stackoverflow Dataset, which provides access to all the stackoverflow data for public repositories - https://console.cloud.google.com/bigquery?ws=!1m4!1m3!3m2!1sbigquery-public-data!2sstackoverflow&project=firstproject-390804 

## Process Outline

**1. Data Collection:** Use stackoverflow public dataset from Google BigQuery
**2. Data Preprocessing:** Out of the 15 tables within the Stack Overflow public dataset, a deliberate selection was made by opting for 6 pertinent tables such as badges, comments, posts_questions, etc., aligning with the project's specific needs. Following this selection, a comprehensive exploratory data analysis was conducted, leading to the transformation of these chosen tables into two optimized entities: Posts and Comments. This transformation process involved the careful elimination of extraneous columns and the mitigation of null values, thereby enhancing the data quality.
**3. Data Pipeline:** In this project, a robust data pipeline is established to execute Extract, Transform, Load (ETL) operations through Airflow. This pipeline orchestrates the extraction of raw data, its transformation to conform to the desired structure, and the loading of cleaned and enriched data into target destinations. Airflow's scheduling capabilities and task dependencies ensure a seamless and automated flow of data, allowing for efficient data processing and maintaining data quality throughout the project lifecycle.
**4. Model Selection:** Selected the models like - SentenceTransformer('distilbert-base-nli-stsb-mean-tokens'), langchain chains summarize, and openAI based on the features that were decided for the streamlit application.
**Topic Relevance Search:** To implement this feature, we harnessed the power of SentenceTransformer with the 'distilbert-base-nli-stsb-mean-tokens' model. This model is chosen for its ability to convert text sentences into meaningful embeddings, capturing semantic context and similarity relationships. Its design, optimized for sentence similarity tasks, aligns perfectly with our project's goal of determining topic relevance by effectively analyzing the textual content of user inputs and matching them with relevant topics in our dataset. The 'distilbert-base-nli-stsb-mean-tokens' model's contextual embeddings enable accurate topic classification and retrieval, enhancing the user experience and search precision.
**Topic Summarization:** With a remarkable ability to generate succinct yet informative summaries from textual content, the advanced language understanding of the text-davinci-003 model effortlessly distills lengthy text into concise insights. This aligns seamlessly with our project's aim to condense topic-related information. By utilizing the text-davinci-003 model, we elevate the accessibility of comprehensive topic insights, enabling users to swiftly grasp crucial concepts and details within the summaries.
**StackAI Generated Answers:** This functionality leverages an openAI - GPT 3.5 Turbo model tailored for generating responses. We opted for this model due to its advanced language generation capabilities, enabling the creation of coherent and contextually relevant answers. By utilizing the openAI model, our project enhances user interactions by providing accurate and informative responses, thereby enriching the overall topic relevance search experience and ensuring users receive comprehensive and precise information.
**5. Data Validation:** Used Great Expectations to validate the gathered data, confirming its conformity to anticipated formats and values.
**6. Backend:** FASTAPI is employed as an intermediary layer between the database and the user interface. It facilitates efficient data retrieval and manipulation by seamlessly connecting with the database, enabling smooth communication and ensuring optimal performance for user interactions.
**7. User Interface:** Develop a web application utilizing Streamlit that offers an instinctive interface enabling users to effortlessly ask a question and view its similar topics and get AI generated answers across various topic categories.
**8. Infrastructure as a Service (IaaS):** Terraform was utilized to establish essential GCP resources including CloudSQL, BigQuery, and compute instances. These resources are seamlessly integrated within the application, enabling automated functionality and streamlining its operational efficiency.
**9. Testing:** Employ pytest and pylint for conducting unit tests, assuring the effectiveness of the application and its integral components.
**10. Deployment:** Deployed the dockerize application in GCP, utilizing Airflow and deployed it using terraform and Airflow. 
**11. Continuous Integration and Continuous Deployment (CI/CD):** Employed GitHub Actions to establish a streamlined CI/CD pipeline, automating integration and deployment tasks. This process is further enhanced through the utilization of Terraform, pytest, and pylint, fostering efficient and consistent application development and delivery.

## Project Setup

<img width="607" alt="image" src="https://user-images.githubusercontent.com/114537365/234988315-a9f89c76-b0ac-413c-9f4b-977eb7c5eab9.png">



## How to run Application locally

To run the application locally, follow these steps:

1. Clone the repository to get all the source code on your machine.

2. Create a virtual environment and install all requirements from the requirements.txt file present.

3. Create a .env file in the root directory with the following variables:

    GITHUB_API_TOKEN: your GitHub API token.

    SNOWFLAKE_USER: your Snowflake username.

    SNOWFLAKE_PASSWORD: your Snowflake password.

    SNOWFLAKE_ACCOUNT: your Snowflake account name.

    SNOWFLAKE_DATABASE: the name of the Snowflake database to use.

    SNOWFLAKE_SCHEMA: the name of the Snowflake schema to use.

    ACESS_TOKEN: Your Github Acess token

    SECRET_KEY: "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" - for JWT Hashing

    ALGORITHM: "HS256" - - for JWT Hashing

    ACCESS_TOKEN_EXPIRE_MINUTES: The expiration time of the access token in minutes

    OPENAI_API_KEY: Your OpenAI API key for accessing the GPT model.

4. Once you have set up your environment variables, start Airflow by running the following command from the root directory:

docker-compose up airflow-init && docker-compose up -d

5. Access the Airflow UI by navigating to http://localhost:8080/ in your web browser.

6. To run the DAGs in Airflow, click on the dags links on the Airflow UI and toggle the switch to enable the DAGs.

7. Once the DAGs have run successfully, start the Streamlit application by running the following command from the streamlit-app directory:

docker-compose up

8. Access the Streamlit UI by navigating to http://localhost:8501/ in your web browser.

9. Enter GitHub username and select a repository from the dropdown menu to view the issues associated with that repository. You can summarize or find similar issues using the options provided on the UI.

## Github Actions - Testing

<img width="1512" alt="image" src="https://user-images.githubusercontent.com/114537365/235001553-2dc11cd4-9131-48d2-a57b-75b302aeb372.png">





