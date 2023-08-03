import openai
openai.api_key = ""
df = pd.read_csv("C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final project\\dataset_converted\\3d_printing\\posts_cleaned.csv")
#comments_df = pd.read_csv("C:\\Users\\Dell\\OneDrive - Northeastern University\\courses\\big data and intl analytics\\DAMG7245-Summer2023\\final project\\dataset_converted\\3d_printing\\comments_cleaned.csv")
#openai embedding using text-embedding model
def get_openai_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

#funcction to combine the text needed to be embeded
def get_combined_text(row):
    title = row['post_title']
    post_body = row['post_body']
    #comments = row['comments']
    tags = row['post_tags']
    combined_text = f"{title} {post_body} {tags}"
    return combined_text
#creating and appending the embedding to df
df['openai_embeddings'] = df.apply(get_combined_text, axis=1).apply(get_openai_embedding)

user_input="what is stl file?"
#euclidian distance - similarity search
def get_most_similar_title(user_input, df):
    user_input_embedding = get_openai_embedding(user_input)
    distances = cdist([user_input_embedding], df['openai_embeddings'].tolist(), metric='euclidean')
    most_similar_index = distances.argmin()
    most_similar_title = df.iloc[most_similar_index]['post_title']
    return most_similar_title

most_similar_title = get_most_similar_title(user_input, df)
print(f"The most similar title is: {most_similar_title}")