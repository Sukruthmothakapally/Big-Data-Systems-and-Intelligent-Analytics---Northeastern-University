import datetime
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import nomic
import os
import pandas as pd
import plotly.express as px
import sys
import time
import warnings

warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from nomic import atlas
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from PIL import Image
from umap import UMAP
import streamlit as st

key = st.session_state.key
endpoint = st.session_state.endpoint

st.title("K-Means Clustering")

def view_image(image_file):
    """
    View image file
    """
    st.image(Image.open(image_file), caption="Image: " + image_file)

IMAGES_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "fashion")
image_files = glob.glob(IMAGES_DIR + "/*")

#sample images
num_images_per_row = 10
num_images_per_col = 5

img_size = 200
start = 500
samples = image_files[start : start + (num_images_per_row * num_images_per_col)]

samples_images = Image.new(
    "RGB", (num_images_per_row * img_size, num_images_per_col * img_size)
)

for idx, image_file in enumerate(samples):
    img = Image.open(image_file)
    img = img.resize((img_size, img_size))
    x = (idx % num_images_per_row) * img_size
    y = (idx // num_images_per_row) * img_size
    samples_images.paste(img, (x, y))


JSON_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "json")
glob.glob(JSON_DIR + "/*.json")

#st.write("Importing vectors embeddings...")

jsonfiles = [entry.name for entry in os.scandir(JSON_DIR) if entry.is_file()]
jsonfiles = [f for f in jsonfiles if os.path.isfile(os.path.join(JSON_DIR, f))]

# Get the most recent file
modification_times = [
    (f, os.path.getmtime(os.path.join(JSON_DIR, f))) for f in jsonfiles
]
modification_times.sort(key=lambda x: x[1], reverse=True)
most_recent_file = JSON_DIR + "/" + modification_times[0][0]

# Loading the most recent file
#print(f"Loading the most recent file of the vector embeddings: {most_recent_file}")

with open(most_recent_file) as f:
    list_emb = json.load(f)

#st.write(f"\nDone: number of imported vector embeddings = {len(list_emb):,}")

#k means clustering title


# Running the kmeans on the images vector embeddings
# and displaying the values of silhouette score
#what is kmeans clustering - https://www.youtube.com/watch?v=4b5d3muPQmA 
k_values = range(2, 10)
silhouette_scores = []
max_val = []

st.write("Performing some K-Means...\n")

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=123456)
    kmeans.fit(list_emb)
    labels = kmeans.labels_
    score = silhouette_score(list_emb, labels)
    max_val.append(score)
    max_val.sort(reverse=True)
    silhouette_scores.append(score)

    st.write(
        f"For k = {k:02} => Silhouette score = {score:.5f} | Maximum score = {max_val[0]:.5f}"
    )

OUTPUT_DIR  = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
plt.figure(figsize=(10, 5))
plt.plot(k_values, silhouette_scores, color="blue")
plt.title("Silhouette scores clustering on images vector embeddings", size=10)
plt.grid(True, color="grey", linestyle="--")

for k, silh in zip(k_values, silhouette_scores):
    plt.text(k, silh, f"{silh:.5f}")

plt.xticks(k_values)
plt.xlabel("Number of clusters (k)")
plt.ylabel("Silhouette score")
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "silhouette_plot.png"))

# Display the plot in Streamlit
st.pyplot(plt)

#
nb_clusters = 17
kmeans = KMeans(n_clusters=nb_clusters, 
                random_state=123456)
kmeans.fit(list_emb)
labels = kmeans.labels_

#
cluster_series = pd.Series(labels, name="cluster")
ax = cluster_series.value_counts().plot(
    kind="bar", figsize=(8, 5), title="Number of images per cluster", color="green")
plt.grid(True, color="grey", linestyle="--")
ax.set_xlabel("Cluster")
ax.set_ylabel("Frequency")
# Display the plot in Streamlit
st.pyplot(plt)

#
df_clusters = pd.DataFrame(
    {"image_file": image_files, "vector": list_emb, "cluster": labels})

#display few clusters
st.write("Displaying few clusters")
# Define number of images to display per cluster
num_images_per_cluster = 5

# Get list of clusters in DataFrame
clusters = df_clusters["cluster"].unique()
# Sorted list
clusters = np.sort(clusters)

# Only include the first 3 clusters
clusters = clusters[:3]

# Create figure with subplots
num_rows = len(clusters)
fig, axes = plt.subplots(num_rows, num_images_per_cluster, figsize=(20, 5*num_rows))

# Display images on subplots
for i, cluster in enumerate(clusters):
    # Get rows in DataFrame for current cluster
    cluster_rows = df_clusters[df_clusters["cluster"] == cluster].head(num_images_per_cluster)
    for j, row in enumerate(cluster_rows.itertuples(index=False)):
        img = Image.open(row.image_file)
        axes[i, j].imshow(img)
        axes[i, j].set_title(f"Cluster {row.cluster}")
        axes[i, j].axis("off")

# Display the plot in Streamlit
st.pyplot(plt)


cluster_labels = [
    "0", "Women's dresses",
    "1", "Denim",
    "2", "Shirt",
    "3", "Full sleeves",
    "4", "Pant",
    "5", "Sun glasses",
    "6", "Shorts",
    "7", "Winter wear",
    "8", "Shoes",
    "9", "Skirt",
    "10", "Kids wear",
    "11", "Lingerie",
    "12", "Accessories",
    "13", "Hoodie",
    "14", "Cloth",
    "15", "Denim shorts",
    "16", "Jacket",
]

cluster_ids = [int(cluster_labels[i]) for i in range(0, len(cluster_labels), 2)]
category_names = [cluster_labels[i + 1] for i in range(0, len(cluster_labels), 2)]

cluster_ids_series = pd.Series(cluster_ids, name="cluster")
cluster_names_series = pd.Series(category_names, name="cluster_label")
cluster_labels_df = pd.concat([cluster_ids_series, cluster_names_series], axis=1)
df_results = pd.merge(df_clusters, cluster_labels_df, on="cluster", how="left")
# Adding 1 to avoid the number 0
df_results["cluster"] = df_results["cluster"].apply(lambda x: int(x) + 1)
# Numbers in 2 characters
df_results["cluster"] = df_results["cluster"].apply(
    lambda x: f"0{x}" if int(x) < 10 else x
)
# Adding some text
df_results["cluster"] = df_results["cluster"].astype(str)
df_results["Cluster and Label"] = (
    "Cluster " + df_results["cluster"] + " = " + df_results["cluster_label"]
)
st.write(df_results.head())

# Saving the results in a json file
df_results.to_json(os.path.join(OUTPUT_DIR, "clusters.json"))

ax = (
    df_results["Cluster and Label"]
    .value_counts()
    .plot(
        kind="barh",
        figsize=(10, 7),
        title="Number of images per cluster",
        color="purple",
    )
)

ax.set_xlabel("cluster")
ax.set_ylabel("Frequency")

#umap clustering
st.write("UMAP clustering")
option = st.radio(
    "How do you want to view the MAP?",
    ("2d", "3d")
)
#print("Running Umap on the images vectors embeddings...")

if option == "2d":

    start = time.time()
    umap_2d = UMAP(n_components=2, init="random", random_state=0)
    proj_2d = umap_2d.fit_transform(list_emb)

    #print("Done")
    elapsed = time.time() - start
    # print(
    #     "Elapsed time: "
    #     + time.strftime(
    #         "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:15], time.gmtime(elapsed)
    #     )
    # )
    #2d projection
    fig_2d = px.scatter(
        proj_2d,
        x=0,
        y=1,
        color=df_results["cluster_label"].tolist(),
        labels={"color": "Cluster"},
        custom_data=[df_results["image_file"].tolist(), df_results["Cluster and Label"].tolist()],
        title="Images Vectors Embeddings UMAP Projections",
        height=640,
    )

    fig_2d.update_traces(marker_size=5, hovertemplate = "%{customdata}")

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig_2d)

else:

#print("Running Umap on the images vectors embeddings...")

    start = time.time()
    umap_3d = UMAP(n_components=3, init="random", random_state=0)
    proj_3d = umap_3d.fit_transform(list_emb)

    #print("Done")
    elapsed = time.time() - start
    # print(
    #     "Elapsed time: "
    #     + time.strftime(
    #         "%H:%M:%S.{}".format(str(elapsed % 1)[2:])[:15], time.gmtime(elapsed)
    #     )
    # )
    clusterlabel = df_results["cluster_label"].tolist()
    fig_3d = px.scatter_3d(
        proj_3d,
        x=0,
        y=1,
        z=2,
        color=clusterlabel,
        labels={"color": "Cluster"},
        custom_data=[df_results["image_file"].tolist(), df_results["Cluster and Label"].tolist()],
        title="Images Vectors Embeddings UMAP Projections",
        height=860,
    )

    fig_3d.update_traces(marker_size=3, hovertemplate = "%{customdata}")
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig_3d)
