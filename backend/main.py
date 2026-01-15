from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import warnings

# Suppress wikipedia parser warning
warnings.filterwarnings("ignore", module="wikipedia")

from search import search_wikipedia, load_kb
from rag import rag_pipeline, run_llm_stream
import database

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
    conversation_id: Optional[str] = None

class Conversation(BaseModel):
    id: str
    title: str
    created_at: str

# Load knowledge base once at startup
kb_texts = load_kb()

# Initialize DB
@app.on_event("startup")
async def startup_db_client():
    await database.init_db()

@app.get("/conversations", response_model=List[Conversation])
async def list_conversations():
    return await database.get_conversations()

@app.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    # Check if conversation exists
    conv = await database.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await database.get_messages(conversation_id)
    return {
        "conversation": conv,
        "messages": messages
    }

@app.post("/conversations", response_model=Conversation)
async def create_new_conversation(data: dict):
    # Optional endpoint to explicitly create a chat
    title = data.get("title", "New Chat")
    cid = await database.create_conversation(title)
    return await database.get_conversation(cid)

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    success = await database.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or could not be deleted")
    return {"status": "success", "id": conversation_id}

@app.post("/ask")
async def ask_ai(query: Query):
    print(f"DEBUG: Received question: {query.question}, conversation_id: {query.conversation_id}")
    
    conversation_id = query.conversation_id
    
    # 1. Handle Conversation Creation
    if not conversation_id:
        # Create new conversation with the current question as title
        # Truncate title if too long
        title = query.question[:50] + "..." if len(query.question) > 50 else query.question
        conversation_id = await database.create_conversation(title)
        print(f"DEBUG: Created new conversation ID: {conversation_id}")
    
    # 2. Save User Message
    await database.add_message(conversation_id, "user", query.question)

    # Fast Path for Greetings
    greetings = {"hello", "hi", "hey", "good morning", "good evening", "greetings"}
    is_greeting = query.question.strip().lower().split()[0] in greetings if query.question.strip() else False
    
    # If strictly just a greeting or very short
    if query.question.strip().lower() in greetings or (len(query.question.split()) < 3 and is_greeting):
        print("DEBUG: Greeting detected. Fast path.")
        
        async def fast_response_wrapper():
            full_response = ""
            async for chunk in run_llm_stream("", query.question, ""):
                full_response += chunk
                yield chunk
            await database.add_message(conversation_id, "ai", full_response)
            
        return StreamingResponse(
            fast_response_wrapper(),
            media_type="text/plain",
            headers={"X-Conversation-ID": str(conversation_id)}
        )

    print("DEBUG: Running step: Search Wikipedia")
    wiki_result = search_wikipedia(query.question)
    
    # 3. Stream & Capture Response
    async def response_wrapper():
        full_response = ""
        # The client needs the ID to continue the chat.
        
        async for chunk in rag_pipeline(wiki_result, kb_texts, query.question):
            full_response += chunk
            yield chunk
            
        # 4. Save AI Response (after stream finishes)
        await database.add_message(conversation_id, "ai", full_response)
        
    return StreamingResponse(
        response_wrapper(),
        media_type="text/plain",
        headers={"X-Conversation-ID": str(conversation_id)}
    )
