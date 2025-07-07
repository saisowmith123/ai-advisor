import os
import faiss
import openai
import pickle
import numpy as np

# 🔐 API Key

# 🧠 Load FAISS index + metadata
index = faiss.read_index("combined_index.index")

with open("course_metadata.pkl", "rb") as f:
    metadata_store = pickle.load(f)

# 🔎 Query embedding
def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# 🔍 Semantic search
def search(query, k=5):
    query_vec = np.array([get_embedding(query)]).astype("float32")
    scores, indices = index.search(query_vec, k)

    results = []
    for idx in indices[0]:
        if idx < len(metadata_store):
            results.append(metadata_store[idx])
    print(results)
    return results