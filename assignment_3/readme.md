# Streamlit app - Azure Computer Vision 4 (Florence) workshop

This is a [Streamlit](./streamlit/) app that uses Azure Computer Vision to analyze images and perform various tasks such as creating embeddings, finding similar images, and clustering images using k-means.

## Features

- **Analyze an image:** The app can analyze an image and extract useful information such as the objects and text present in the image. This is done using the Azure Computer Vision API, which can detect and recognize objects, landmarks, text, and more in images.

- **Create embeddings:** The app can create embeddings for all the images in a dataset. These embeddings represent the images in a lower-dimensional space and can be used for tasks such as finding similar images. The embeddings are created using a pre-trained neural network that has been trained to extract useful features from images.

- **Find similar images:** The app allows users to find similar images based on an input image or user-defined criteria. This is done by comparing the embeddings of the images and finding the ones that are closest to the input. The app uses a nearest neighbors algorithm to efficiently search for the most similar images in the dataset.

- **Cluster images using k-means:** The app can cluster images using the k-means algorithm. This groups similar images together into clusters, making it easier to explore and analyze large datasets. The k-means algorithm works by iteratively assigning each image to the cluster with the nearest mean, then updating the cluster means based on the new assignments.

## Deployment

The Streamlit app has been dockerized, which means that it can be easily deployed and run on any platform that supports Docker. To run the app locally using Docker, you will need to have Docker installed on your machine. Then, you can follow these steps:

1. Build the Docker image by running the `docker build` command from within the `streamlit` directory:
   ```bash
    docker build -t my-streamlit-app .
   ```

2. Run a container from the image by running the `docker run` command:
   ```bash
    docker run -p 8090:8090 my-streamlit-app
   ```

3. Access your Streamlit app by visiting `http://localhost:8090` in your web browser.


## Cloud hosting
The Streamlit app is also hosted on Google Cloud Platform (GCP) at IP address '34.23.24.122' which makes it easy to deploy and scale the app as needed.
- Streamlit: `8090`

## Azure Keys and Endpoint

In order to use the Azure Computer Vision API in your Streamlit app, you will need to obtain an API key and endpoint from Azure. Here are the steps to do this:

1. Sign in to the [Azure portal](https://portal.azure.com/) using your Microsoft account.

2. In the left-hand menu, click on "Create a resource".

3. Search for "Cognitive Services" and click on the "Create" button.

4. Fill in the required information, such as the name, subscription, resource group, and location of your Cognitive Services resource.

5. Under "Resource type", select "Computer Vision".

6. Click on the "Review + create" button, then click on "Create" to create your Cognitive Services resource.

7. Once your resource has been created, go to the "Keys and Endpoint" page of your resource.

8. Copy the value of "Key1" or "Key2". This is your Azure Computer Vision API key.

9. Copy the value of "Endpoint". This is your Azure Computer Vision API endpoint.

You will need to provide these values to your Streamlit app in order to use the Azure Computer Vision API. You can do this by setting environment variables or by passing them as arguments when running your app.


## Additional Resources

For more detailed information about the project, including snapshots of the working application, please refer to [codelab](https://codelabs-preview.appspot.com/?file_id=1jnmISjl4bqLAJlhWXvqKj_8e2liZOaHPRmzbPqo4kLo#0)


## Authors

- Riya
- Sukruth
- Vedant


## References

This app was built using the [Azure Computer Vision Workshop](https://github.com/Azure/gen-cv/tree/main/azure_computer_vision_workshop) as a reference.
