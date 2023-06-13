from sentence_transformers import SentenceTransformer
import numpy as np

sbert_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_text(text):
    text = text.replace("\n", " ")
    return sbert_model.encode([text])

def get_top_k_similar_sentences(original_sentences, user_input, k=5):
    original_embeddings = [embed_text(sentence) for sentence in original_sentences]
    user_input_embedding = embed_text(user_input)
    similarities = [np.dot(user_input_embedding.reshape(-1), original_embedding.reshape(-1)) for original_embedding in original_embeddings]
    top_k_indices = np.argsort(similarities)[-k:]
    return [original_sentences[i] for i in top_k_indices]

# Example usage
original_text = "Thank you, Whitley.Good afternoon and thank you for joining us on our Q4 2014 conference call.Joining me on today's call is our Chairman and CEO <UNK> <UNK> and our President <UNK> <UNK>. Before we begin, I will read our Safe Harbor statement. Today we will make some forward-looking statements, the accuracy of which is subject to risks and uncertainties.Wherever possible, we will try to identify those forward-looking statements by using words such as believe, expect, anticipate, forecast, and similar expressions. Our forward-looking statements are based on our estimates and assumptions as of today, February 25, 2015, and should not be relied upon as representing our estimates or views on any subsequent date. Please refer to the cautionary statement regarding forward-looking information and the risk factors in our most recent 10-K and subsequent SEC filings, including disclosure of the factors that could cause results to differ materially from those expressed or implied. During this call, we will discuss non-GAAP financial measures, which include organic sales and growth numbers, as well as EBITDA" # List of sentences from the company's earnings call transcript
original_sentences = original_text.split('. ')
user_input = "how are the earnings for q4?" # User input
top_5_similar_sentences = get_top_k_similar_sentences(original_sentences, user_input)
for i, sentence in enumerate(top_5_similar_sentences):
    print(f"{i+1}. {sentence}")
