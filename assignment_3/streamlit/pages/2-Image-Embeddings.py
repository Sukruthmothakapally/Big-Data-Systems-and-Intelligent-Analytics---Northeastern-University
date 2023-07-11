import datetime
import glob
import json
import multiprocessing
import numpy as np
import nomic
import os
import plotly.express as px
import sys
import time

from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from nomic import atlas
from PIL import Image
from tqdm import tqdm
from umap import UMAP
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st
import requests


key = st.session_state.key
endpoint = st.session_state.endpoint

def image_embedding_batch(image_file):
    """
    Embedding image using Azure Computer Vision 4 Florence
    """
    version = "?api-version=2023-02-01-preview&modelVersion=latest"
    vec_img_url = endpoint + "/computervision/retrieval:vectorizeImage" + version

    headers_image = {
        'Content-type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': key
    }

    with open(image_file, 'rb') as f:
        data = f.read()

    try:
        r = requests.post(vec_img_url, data=data, headers=headers_image)
        image_emb = r.json()['vector']
        return image_emb, r
    except Exception as e:
        st.write(f"An error occurred while processing {image_file}: {e}")
        return None, None

def view_image(image_file):
    """
    View image file
    """
    plt.imshow(Image.open(image_file))
    plt.axis('off')
    plt.title("Image: " + image_file, fontdict={'fontsize': 10})
    plt.show()


IMAGES_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "fashion")

image_files = glob.glob(IMAGES_DIR + "/*")

#st.write("Directory of images:", IMAGES_DIR)
st.write("Total number of catalog images =", "{:,}".format(len(image_files)))

def process_image(image_file, max_retries=20):
    """
    Process image with error management
    """
    num_retries = 0

    while num_retries < max_retries:
        try:
            embedding, response = image_embedding_batch(image_file)

            if response.status_code == 200:
                return embedding

            else:
                num_retries += 1
                st.write(
                    f"Error processing {image_file}: {response.status_code}.\
                Retrying... (attempt {num_retries} of {max_retries})"
                )

        except Exception as e:
            st.write(f"An error occurred while processing {image_file}: {e}")
            st.write(f"Retrying... (attempt {num_retries} of {max_retries})")
            num_retries += 1

    return None

def process_all_images(image_files, max_workers=4, max_retries=20):
    """
    Running the full process using pool
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        embeddings = list(
            tqdm(
                executor.map(lambda x: process_image(x, max_retries), image_files),
                total=len(image_files),
            )
        )

    return [emb for emb in embeddings if emb is not None]

if image_files:
    st.write("Starting to compute vector embeddings for our", "{:,}".format(len(image_files)), "catalog images...")
    start = time.time()

    # Running the images vector embeddings for all the images files
    list_emb = process_all_images(image_files, max_workers=4, max_retries=20)

    # End of job
    #st.write("Done")
    elapsed = time.time() - start
    st.write(f"\nElapsed time: {int(elapsed / 60)} minutes, {int(elapsed % 60)} seconds")
    st.write("Number of processed images =", len(list_emb))
    #st.write(f"Processing time per image = {(elapsed / len(list_emb)):.5f} sec")

#display number of vector embeddings
st.write("Number of vector embeddings =", len(list_emb))
#st.write(f"Number of images files = {len(image_files)}")

#st.write("Creating JSON directory")

JSON_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "json")
os.makedirs(JSON_DIR, exist_ok=True)

#st.write("Exporting images vector embeddings")

# Json filename
current_dt = str(datetime.datetime.today().strftime("%d%b%Y_%H%M%S"))
json_file = os.path.join(JSON_DIR, f"img_embed_{current_dt}.json")

# Saving vectors embeddings into this Json file
with open(json_file, "w") as f:
    json.dump(list_emb, f)

#st.write("Done. Vector embeddings have been saved in:", json_file)


#st.write("Importing vectors embeddings...")

#JSON_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "json")

jsonfiles = [entry.name for entry in os.scandir(JSON_DIR) if entry.is_file()]
jsonfiles = [f for f in jsonfiles if os.path.isfile(os.path.join(JSON_DIR, f))]

# Get the most recent file
modification_times = [
    (f, os.path.getmtime(os.path.join(JSON_DIR, f))) for f in jsonfiles
]
modification_times.sort(key=lambda x: x[1], reverse=True)
most_recent_file = JSON_DIR + "/" + modification_times[0][0]

# Loading the most recent file
#st.write(f"Loading the most recent file of the vector embeddings: {most_recent_file}")

with open(most_recent_file) as f:
    list_emb = json.load(f)

#st.write(f"\nDone: number of imported vector embeddings = {len(list_emb):,}")

#UMAP
plot_type = st.selectbox("Select plot type", ["2D", "3D"])

if plot_type == "2D":

    st.write("Running Umap on the images vectors embeddings...")

    start = time.time()
    umap_2d = UMAP(n_components=2, init="random", random_state=0)
    proj_2d = umap_2d.fit_transform(list_emb)

    st.write("Done")
    elapsed = time.time() - start
    st.write(
        "Elapsed time: "
        + time.strftime(
            "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:15], time.gmtime(elapsed)
        )
    )

    x = proj_2d[:, 0]
    y = proj_2d[:, 1]

    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title("Images Vectors Embeddings UMAP Projections")
    st.pyplot(fig)
else:
    st.write("Running Umap on the images vectors embeddings...")

    start = time.time()
    umap_3d = UMAP(n_components=3, init="random", random_state=0)
    proj_3d = umap_3d.fit_transform(list_emb)

    st.write("Done")
    elapsed = time.time() - start
    st.write(
        "Elapsed time: "
        + time.strftime(
            "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:15], time.gmtime(elapsed)
        )
    )

    #st.write("Plotting the 3D projection of the images vectors embeddings")
    x = proj_3d[:, 0]
    y = proj_3d[:, 1]
    z = proj_3d[:, 2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z)
    ax.set_title("Images Vectors Embeddings UMAP Projections")
    st.pyplot(fig)


    
