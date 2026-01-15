import os
import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Optional

# Default to localhost if not set
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "kai_db"

client = None
db = None

async def init_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Optional: Ping to verify connection
    try:
        await client.admin.command('ping')
        print(f"DEBUG: Connected to MongoDB at {MONGO_URL}")
    except Exception as e:
        print(f"ERROR: Could not connect to MongoDB: {e}")

async def create_conversation(title: str) -> str:
    result = await db.conversations.insert_one({
        "title": title,
        "created_at": datetime.utcnow()
    })
    return str(result.inserted_id)

async def add_message(conversation_id: str, role: str, content: str):
    await db.messages.insert_one({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow()
    })

async def get_conversations() -> List[Dict]:
    cursor = db.conversations.find().sort("created_at", -1)
    results = []
    async for document in cursor:
        document["id"] = str(document.pop("_id"))
        if isinstance(document.get("created_at"), datetime):
             document["created_at"] = document["created_at"].isoformat()
        results.append(document)
    return results

async def get_messages(conversation_id: str) -> List[Dict]:
    cursor = db.messages.find({"conversation_id": conversation_id}).sort("created_at", 1)
    results = []
    async for document in cursor:
        document["id"] = str(document.pop("_id"))
        if isinstance(document.get("created_at"), datetime):
             document["created_at"] = document["created_at"].isoformat()
        results.append(document)
    return results

async def get_conversation(conversation_id: str) -> Optional[Dict]:
    try:
        document = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if document:
            document["id"] = str(document.pop("_id"))
            if isinstance(document.get("created_at"), datetime):
                document["created_at"] = document["created_at"].isoformat()
            return document
    except:
        return None
    return None

async def delete_conversation(conversation_id: str) -> bool:
    try:
        # Delete messages first
        await db.messages.delete_many({"conversation_id": conversation_id})
        # Delete conversation
        result = await db.conversations.delete_one({"_id": ObjectId(conversation_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"ERROR: Failed to delete conversation {conversation_id}: {e}")
        return False
