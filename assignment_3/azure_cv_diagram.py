from diagrams import Cluster, Diagram, Edge
from diagrams.azure.compute import VM
from diagrams.azure.ml import CognitiveServices
from diagrams.azure.storage import BlobStorage
from diagrams.gcp.compute import ComputeEngine
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow

with Diagram("Azure Computer Vision Workshop", show=True):
    user = User("User")
    gcp = ComputeEngine("Google Cloud Platform")
    docker = Docker("Dockerized Streamlit App")
    azure_keys = VM("Azure Keys and Endpoint")
    image_analysis = CognitiveServices("Image Analysis")
    vector_embeddings = VM("Vector Embeddings")
    k_means_clustering = VM("K-Means Clustering")

    with Cluster("Similar Images"):
        search_by_user_input = VM("Search by User Input")
        search_by_image = VM("Search by Image")
    
    #cluster for 2d and 3d plots
    with Cluster("plots"):
        plots_2d = VM("2D Plots")
        plots_3d = VM("3D Plots")

    user >> gcp >> docker >> azure_keys >> image_analysis >> vector_embeddings >> [search_by_user_input, search_by_image, k_means_clustering]
    k_means_clustering >> [plots_2d, plots_3d]
