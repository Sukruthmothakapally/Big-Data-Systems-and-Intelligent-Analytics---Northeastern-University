import numpy as np

def get_top_k_similar_sentences(original_sentences, user_input_embedding, k=5):
    similarities = [np.dot(user_input_embedding, original_embedding) for original_embedding in openai_embeddings]
    top_k_indices = np.argsort(similarities)[-k:]
    top_k_similarities = [similarities[i] for i in top_k_indices]
    return [(original_sentences[i], similarity) for i, similarity in zip(top_k_indices, top_k_similarities)]

# Hard-coded values for the OpenAI embeddings and the original text
openai_embeddings = np.array([-1.0842022e-19, -3.8232845e-01, 0.0000000e+00, -1.1818620e+00, -0.0000000e+00, -1.1315948e+00])
original_text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence. This is the sixth sentence."
original_sentences = original_text.split('. ')

# User-provided input
user_input = input("Enter a sentence to compare with the embeddings: ")
user_input_embedding = np.array([float(x) for x in input("Enter the embedding of the user input (space-separated values): ").split()])

# Find and display the top 5 similar sentences
top_5_similar_sentences_and_scores = get_top_k_similar_sentences(original_sentences, user_input_embedding)
for i, (sentence, score) in enumerate(top_5_similar_sentences_and_scores):
    print(f"{i+1}. {sentence} (Similarity score: {score:.2f})")
