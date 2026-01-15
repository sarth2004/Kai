from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from search import search_wikipedia, load_kb
from rag import rag_pipeline

app = FastAPI(title="Educational AI Assistant - Code Generation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str


# Load knowledge base once at startup
kb_texts = load_kb()


@app.post("/ask")
async def ask_ai(query: Query):
    print(f"DEBUG: Received question: {query.question}")
    print("DEBUG: Running step: Search Wikipedia")
    wiki_result = search_wikipedia(query.question)
    
    return StreamingResponse(
        rag_pipeline(wiki_result, kb_texts, query.question),
        media_type="text/plain"
    )
