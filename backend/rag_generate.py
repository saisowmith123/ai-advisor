import openai
from chatbot_search import search


# 🔐 API Key (replace with your key)

def format_context(docs):
    parts = []
    for doc in docs:
        if doc["type"] == "course":
            parts.append(f"[Course: {doc['courseId']}]\n{doc['text']}")
        elif doc["type"] == "requirement":
            parts.append(f"[Requirement: {doc['text']}")
    
    # print(parts)
    return "\n\n".join(parts)


