#top 5 senteces using openai

import openai
import numpy as np
openai.api_key = "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"

def embed_text(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def get_top_k_similar_sentences(original_sentences, user_input, k=5):
    original_embeddings = [embed_text(sentence) for sentence in original_sentences]
    user_input_embedding = embed_text(user_input)
    similarities = [np.dot(user_input_embedding, original_embedding) for original_embedding in original_embeddings]
    top_k_indices = np.argsort(similarities)[-k:]
    return [original_sentences[i] for i in top_k_indices]

# Example usage
original_text = "Thank you, Whitley.Good afternoon and thank you for joining us on our Q4 2014 conference call.Joining me on today's call is our Chairman and CEO <UNK> <UNK> and our President <UNK> <UNK>. Before we begin, I will read our Safe Harbor statement. Today we will make some forward-looking statements, the accuracy of which is subject to risks and uncertainties.Wherever possible, we will try to identify those forward-looking statements by using words such as believe, expect, anticipate, forecast, and similar expressions. Our forward-looking statements are based on our estimates and assumptions as of today, February 25, 2015, and should not be relied upon as representing our estimates or views on any subsequent date. Please refer to the cautionary statement regarding forward-looking information and the risk factors in our most recent 10-K and subsequent SEC filings, including disclosure of the factors that could cause results to differ materially from those expressed or implied. During this call, we will discuss non-GAAP financial measures, which include organic sales and growth numbers, as well as EBITDA" # List of sentences from the company's earnings call transcript
original_sentences = original_text.split('. ')
user_input = "how are they estimates for q4" # User input
top_5_similar_sentences = get_top_k_similar_sentences(original_sentences, user_input)
for i, sentence in enumerate(top_5_similar_sentences):
    print(f"{i+1}. {sentence}")

