from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import uuid
import openai
import json
from chatbot_search import search
from rag_generate import format_context

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Set OpenAI API key here

# 🧠 In-memory session store
chat_sessions = {}
chat_sessions_fe = {}
chat_log_store = {}  # Optional: to log and persist chat history

# @app.post("/chat")
# def chat_with_ai(
#     query: str = Form(...),
#     session_id: str = Form(None)
# ):
#     # 🆕 Create new session if needed
#     if not session_id or session_id not in chat_sessions:
#         session_id = str(uuid.uuid4())
#         chat_sessions[session_id] = [
#             {"role": "system", "content": "You are a helpful academic advisor for the M.S. in Computer Science program."}
#         ]

#     # ➕ Append user query
#     chat_sessions[session_id].append({"role": "user", "content": query})
#     print(query)

#     # 🔍 Retrieve top matching documents (courses + requirements)
#     top_docs = search(query, k=5)
    
#     context = format_context(top_docs)
    

#     # 🧠 Rewrite user message with context
#     user_prompt = f'''
# Student asked: "{query}"

# Below is relevant information from course catalog and degree requirements:
# {context}

# Please give a clear and helpful response to guide the student in selecting the right course(s). 

# '''.strip()

#     chat_sessions[session_id][-1]["content"] = user_prompt

#     # 🤖 Call GPT
#     response = openai.chat.completions.create(
#         model="gpt-4",
#         messages=chat_sessions[session_id],
#         temperature=0.7,
#     )

#     reply = response.choices[0].message.content

#     # ➕ Append assistant reply to session
#     chat_sessions[session_id].append({"role": "assistant", "content": reply})

#     # 📦 Log conversation for analysis (optional)
#     chat_log_store[session_id] = chat_sessions[session_id]
#     with open("chat_logs.json", "w") as f:
#         json.dump(chat_log_store, f, indent=2)

#     return {
#         "reply": reply,
#         "session_id": session_id
#     }
@app.get("/chat/{session_id}")
def get_chat_session(session_id: str):
    # Check if the session ID exists
    if session_id not in chat_sessions_fe:
        return {"error": "Session ID not found"}, 404

    # Return the chat session messages
    return {"session_id": session_id, "messages": chat_sessions_fe[session_id]}


@app.post("/chat")
def chat_with_ai(
    query: str = Form(...),
    session_id: str = Form(None)
):
    query = query.strip()
    # 🆕 Create new session if needed
    if not session_id or session_id not in chat_sessions:
        # Generate a new session ID if none exists or if the session is not found
        session_id = session_id or str(uuid.uuid4())
        # Initialize the session with a system message
        chat_sessions[session_id] = [
            {"role": "system", "content": "You are a helpful academic advisor for the M.S. in Computer Science program."}
        ]
        chat_sessions_fe[session_id] = [
            {"role": "system", "content": "You are a helpful academic advisor for the M.S. in Computer Science program."}
        ]
        print(f"New session started: {session_id}")

    # ➕ Append user query
    chat_sessions[session_id].append({"role": "user", "content": query})
    chat_sessions_fe[session_id].append({"role": "user", "content": query})
    print(f"User query added: {query}")

    # 🔍 Retrieve top matching documents (courses + requirements)
    top_docs = search(query, k=5)
    context = format_context(top_docs)
    
    # 🧠 Rewrite user message with context (provide context to the AI for better responses)
    user_prompt = f'''
Student query: "{query}"

Context: 
The following information is from the course catalog, degree requirements, and historical enrollment data (including average grades and fill rates).
{context}

Your task:
Provide a clear, concise, and structured recommendation to help the student choose suitable course(s). Structure your response using bullet points or short paragraphs.

Make sure to:
- Directly address the student’s query.
- Highlight course relevance to the student’s academic or career goals (if evident).
- Compare courses where applicable, focusing on:
  • grades distribution per instructor (difficulty/ease of getting good grades)
  • Fill rate (likelihood of securing a seat)
  • Prerequisites or restrictions
  • Number of credits obtained if i take this course
- Recommend the most suitable course(s) and explain why.
'''

    # ➕ Append the new user prompt to the session's conversation
    chat_sessions[session_id].append({"role": "user", "content": user_prompt})
    print(f"User prompt appended with context.")

    # 🧠 Call OpenAI GPT-4 API with the full conversation history
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=chat_sessions[session_id],  # Pass the full session history
        temperature=0.7,
    )

    # Get the assistant's reply
    reply = response.choices[0].message.content
    print(f"Assistant reply: {reply}")

    # ➕ Append assistant reply to session
    chat_sessions[session_id].append({"role": "assistant", "content": reply})
    chat_sessions_fe[session_id].append({"role": "assistant", "content": reply})


    return {
        "reply": reply,
        "session_id": session_id
    }
