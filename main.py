from fastapi import FastAPI
from pydantic import BaseModel
import os
import pickle
import faiss
import google.generativeai as genai

# ✅ Configure Gemini API Key (from Railway environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# ✅ Load FAISS index & chunks
INDEX_PATH = "chunks/index.faiss"
CHUNKS_PATH = "chunks/chunks.pkl"

if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
else:
    index = None
    chunks = []

# ✅ FastAPI App
app = FastAPI(title="Ask Babasaheb API")

class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "✅ Ask Babasaheb Backend is Running!"}

@app.post("/ask")
def ask_question(query: Query):
    # Temporary: just use top 3 chunks for now
    if not chunks:
        docs = "No data found. Please upload FAISS index."
    else:
        docs = " ".join([c['text'] for c in chunks[:3]])

    prompt = f"""
    Answer strictly from Babasaheb Ambedkar's verified writings below:
    {docs}

    Question: {query.question}

    If unrelated, respond:
    "I can only answer from Babasaheb's verified writings."
    """

    response = model.generate_content(prompt)
    return {
        "answer": response.text,
        "sources": [
            {
                "source": "Volume 1",
                "pdf_page": 15,
                "link": "/pdfs/vol1.pdf"
            }
        ]
    }
