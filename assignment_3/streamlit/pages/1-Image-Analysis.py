import streamlit as st
from cleanvision.imagelab import Imagelab
from PIL import Image
import requests
import os
import pandas as pd
import threading

key = st.session_state.key
endpoint = st.session_state.endpoint

def view_image(image_file):
    """
    View image file
    """
    st.image(Image.open(image_file), caption="Image: " + image_file)

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

    st.write("Automatic analysis of the image using Azure Computer Vision 4.0:")
    st.markdown(f"""
<style>
    .caption-box {{
        border: 5px solid red;
        padding: 10px;
        display: inline-block;
    }}
    .small-font {{
        font-size: 0.8em;
    }}
</style>
### Main caption : <span class="caption-box">{results['captionResult']['text']} <span class="small-font">(Confidence =</span> {results['captionResult']['confidence']:.3f})</span>
""", unsafe_allow_html=True)

    st.write("   Detected tags:")
    
    tags_data = [{'Tag': tag['name'], 'Confidence': tag['confidence']} for tag in results['tagsResult']['values']]
    
    tags_df = pd.DataFrame(tags_data)
    
    st.table(tags_df)


image_extensions = [".jpg", ".jpeg", ".png"]

IMAGES_DIR = os.path.join("..", "gen-cv", "azure_computer_vision_workshop", "fashion")

image_files = [
    os.path.join(IMAGES_DIR, f)
    for f in os.listdir(IMAGES_DIR)
    if os.path.splitext(f)[1] in image_extensions
]

idx = st.number_input("Enter the index of the image you want to view", min_value=0, max_value=len(image_files)-1, step=1)

view_image(image_files[int(idx)])
describe_image_with_AzureCV4(image_files[int(idx)])