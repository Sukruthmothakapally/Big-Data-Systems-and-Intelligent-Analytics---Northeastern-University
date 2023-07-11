import datetime
import glob
import json
import os
import random
import sys
import time
from dotenv import load_dotenv
from PIL import Image

import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import requests
import seaborn as sns
from PIL import Image
import streamlit as st

key = st.session_state.key
endpoint = st.session_state.endpoint

def view_image(image_file):
    """
    View image file
    """
    st.image(Image.open(image_file), caption="Image: " + image_file)

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

def get_similar_images_using_image(list_emb, image_files, image_file):
    """
    Get similar images using an image with Azure Computer Vision 4 Florence
    """
    ref_emb = image_embedding(image_file)
    idx = 0
    results_list = []

    for emb_image in list_emb:
        simil = get_cosine_similarity(ref_emb, list_emb[idx])
        results_list.append(simil)
        idx += 1

    df_files = pd.DataFrame(image_files, columns=['image_file'])
    df_simil = pd.DataFrame(results_list, columns=['similarity'])
    df = pd.concat([df_files, df_simil], axis=1)
    df.sort_values('similarity',
                   axis=0,
                   ascending=False,
                   inplace=True,
                   na_position='last')

    return df


def get_similar_images_using_prompt(prompt, image_files, list_emb):
    """
    Get similar umages using a prompt with Azure Computer Vision 4 Florence
    """
    prompt_emb = text_embedding(prompt)
    idx = 0
    results_list = []

    for emb_image in list_emb:
        simil = get_cosine_similarity(prompt_emb, list_emb[idx])
        results_list.append(simil)
        idx += 1

    df_files = pd.DataFrame(image_files, columns=['image_file'])
    df_simil = pd.DataFrame(results_list, columns=['similarity'])
    df = pd.concat([df_files, df_simil], axis=1)
    df.sort_values('similarity',
                   axis=0,
                   ascending=False,
                   inplace=True,
                   na_position='last')

    return df

def remove_background(image_file):
    """
    Removing background from an image file using Azure Computer Vision 4
    """
    remove_background_url = endpoint +\
    "/computervision/imageanalysis:segment?api-version=2023-02-01-preview&mode=backgroundRemoval"

    headers_background = {
        'Content-type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': key
    }

    #st.write("Removing background from the image using Azure Computer Vision 4.0..."# )

    with open(image_file, 'rb') as f:
        data = f.read()

    r = requests.post(remove_background_url, data=data, headers=headers_background)

    output_image = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "without_background.jpg")
    with open(output_image, 'wb') as f:
        f.write(r.content)

    #display output image on streamlit
    #st.image(Image.open(output_image), caption="Image: " + output_image)

    return output_image



def side_by_side_images(image_file1, image_file2):
    """
    Display two images side by side
    """
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(plt.imread(image_file1))
    ax[1].imshow(plt.imread(image_file2))
    
    for i in range(2):
        ax[i].axis('off')
        ax[i].set_title(['Initial image', 'Without the background'][i])
    fig.suptitle('Background removal with Azure Computer Vision 4', fontsize=11)
    # st.pyplot(fig)
    #plt.tight_layout()
    #plt.show()


def describe_image_with_AzureCV4(image_file):
    """
    Get tags & caption from an image using Azure Computer Vision 4 Florence
    """
    options = "&features=tags,caption"
    model = "?api-version=2023-02-01-preview&modelVersion=latest"
    url = endpoint + "/computervision/imageanalysis:analyze" + model + options

    headers_cv = {
        'Content-type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': key
    }

    with open(image_file, 'rb') as f:
        data = f.read()

    r = requests.post(url, data=data, headers=headers_cv)
    results = r.json()

#     st.write("Automatic analysis of the image using Azure Computer Vision 4.0:")
#     st.markdown(f"""
# <style>
#     .caption-box {{
#         border: 5px solid red;
#         padding: 10px;
#         display: inline-block;
#     }}
#     .small-font {{
#         font-size: 0.8em;
#     }}
# </style>
# ### Main caption : <span class="caption-box">{results['captionResult']['text']} <span class="small-font">(Confidence =</span> {results['captionResult']['confidence']:.3f})</span>
# """, unsafe_allow_html=True)

#     st.write("   Detected tags:")
    
    tags_data = [{'Tag': tag['name'], 'Confidence': tag['confidence']} for tag in results['tagsResult']['values']]
    
    tags_df = pd.DataFrame(tags_data)
    
    # st.table(tags_df)

def get_results_using_image(reference_image, nobackground_image,
                            image_files, list_emb, topn, disp=False):
    """
    Get the topn results from a visual search using an image
    Will generate a df, display the topn images and return the df
    """
    df = get_similar_images_using_image(list_emb, image_files, nobackground_image)
    df.head(topn).style.background_gradient(
        cmap=sns.light_palette("green", as_cmap=True))
  
    topn_list, simil_topn_list = get_topn_images(df, topn, disp=disp)
    nb_cols = 3
    nb_rows = (topn + nb_cols - 1) // nb_cols
    view_similar_images_using_image(reference_image, topn_list, simil_topn_list, 
                                    num_cols=nb_cols, num_rows=nb_rows)

    return df


def get_results_using_prompt(query, image_files, list_emb, topn, disp=False):
    """
    Get the topn results from a visual search using a text query
    Will generate a df, display the topn images and return the df
    """
    df = get_similar_images_using_prompt(query, image_files, list_emb)
    df.head(topn).style.background_gradient(
        cmap=sns.light_palette("green", as_cmap=True))
  
    topn_list, simil_topn_list = get_topn_images(df, topn, disp=disp)
    nb_cols = 3
    nb_rows = (topn + nb_cols - 1) // nb_cols
    view_similar_images_using_prompt(query, topn_list, simil_topn_list, 
                                    num_cols=nb_cols, num_rows=nb_rows)

    return df

def get_topn_images(df, topn=5, disp=False):
    """
    Get topn similar images
    """
    idx = 0
    if disp:
        #display top 3 images text in bigger font
        st.markdown(f"<h2 style='font-size: 24px;'>Top {topn} images:</h2>", unsafe_allow_html=True)

    topn_list = []
    simil_topn_list = []

    table_data = []

    while idx < topn:
        row = df.iloc[idx]
        if disp:
            table_data.append([idx+1, row['image_file'], row['similarity']])
        topn_list.append(row['image_file'])
        simil_topn_list.append(row['similarity'])
        idx += 1

    if disp:
        st.table(pd.DataFrame(table_data, columns=["Rank", "Filename", "Similarity Score"]))

    return topn_list, simil_topn_list


def image_embedding(image_file):
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
    r = requests.post(vec_img_url, data=data, headers=headers_image)
    image_emb = r.json()['vector']

    return image_emb

def text_embedding(promptxt):
    """
    Embedding text using Azure Computer Vision 4 Florence
    """
    version = "?api-version=2023-02-01-preview&modelVersion=latest"
    vec_txt_url = endpoint + "/computervision/retrieval:vectorizeText" + version

    headers_prompt = {
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Key': key
    }

    prompt = {'text': promptxt}
    r = requests.post(vec_txt_url,
                      data=json.dumps(prompt),
                      headers=headers_prompt)
    text_emb = r.json()['vector']

    return text_emb

def view_similar_images_using_image(reference_image, topn_list, 
                                    simil_topn_list, num_rows=2, num_cols=3):
    """
    Plot similar images using an image with Azure Computer Vision 4 Florence
    """
    img_list = topn_list
    if img_list[0] != reference_image:
        img_list.insert(0, reference_image)

    num_images = len(img_list)
    FIGSIZE = (12, 8)
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=FIGSIZE)

    size = 8 if num_rows >= 3 else 10

    for i, ax in enumerate(axes.flat):
        if i < num_images:
            img = mpimg.imread(img_list[i])
            ax.imshow(img)

            if i == 0:
                imgtitle = f"Image to search:\n {os.path.basename(img_list[i])}"
                ax.set_title(imgtitle, size=size, color='blue')
            else:
                imgtitle = f"Top {i}: {os.path.basename(img_list[i])}\nSimilarity = {round(simil_topn_list[i-1], 5)}"
                ax.set_title(imgtitle, size=size, color='green')
            ax.axis('off')

        else:
            ax.axis('off')
    st.pyplot(fig)
    #plt.show()
    
    #print("\033[1;31;32m",
         # datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          #"Powered by Azure Computer Vision Florence")


def view_similar_images_using_prompt(query, topn_list, simil_topn_list,
                                     num_rows=2, num_cols=3):
    """
    Plot similar images using a prompt with Azure Computer Vision 4 Florence
    """
    #print("\033[1;31;34m")
    #st.write("Similar images using query =", query)
    
    num_images = len(topn_list)
    FIGSIZE = (12, 8)
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=FIGSIZE)

    size = 8 if num_rows >= 3 else 10

    for i, ax in enumerate(axes.flat):
        if i < num_images:
            img = mpimg.imread(topn_list[i])
            ax.imshow(img)
            imgtitle = f"Top {i+1}: {os.path.basename(topn_list[i])}\nSimilarity = {round(simil_topn_list[i], 5)}"
            ax.set_title(imgtitle, size=size, color='green')
            ax.axis('off')

        else:
            ax.axis('off') 
    st.pyplot(fig)
    #plt.show()
    
    # print("\033[1;31;32m",
    #       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #       "Powered by Azure Computer Vision Florence")

def get_cosine_similarity(vector1, vector2):
    """
    Get cosine similarity value between two embedded vectors
    Using sklearn
    """
    dot_product = 0
    length = min(len(vector1), len(vector2))

    for i in range(length):
        dot_product += vector1[i] * vector2[i]

    cosine_similarity = dot_product / (math.sqrt(sum(x * x for x in vector1))\
                                       * math.sqrt(sum(x * x for x in vector2)))

    return cosine_similarity


IMAGES_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "fashion")
image_files = glob.glob(IMAGES_DIR + "/*")

#sample images
num_images_per_row = 10
num_images_per_col = 5

img_size = 200
start = 1000
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

TEST_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "test")
test_images = glob.glob(f"{TEST_DIR}/*")

#user should have option to either get similar images using an image or using a prompt

option = st.radio(
    "How would you like to get similar images?",
    ("Get similar images using an image", "Get similar images using a prompt")
)

if option == "Get similar images using an image":
    #if user selects to get similar images using an image -
    #user can select any one of the test images from test_dir using select box 
    reference_image = st.selectbox(
    "Select a test image",
    test_images)
    #reference_image = test_images[0] #modify accordingly based on the test image selected

    view_image(reference_image)
    describe_image_with_AzureCV4(reference_image)

    #removes background from the image
    nobackground_image = remove_background(reference_image)
    side_by_side_images(reference_image, nobackground_image)

    #displays the top 3 similar images using an image
    get_results_using_image(
        reference_image, nobackground_image, image_files, list_emb, topn=3, disp=True
    )

else:
    #else if user selects to get similar images using a prompt -
    #user can enter a prompt in the text box
    query = st.text_input("Enter your query")
    #displays the top 3 similar images using a prompt
    if query:
        get_results_using_prompt(query, image_files, list_emb, topn=3, disp=False)