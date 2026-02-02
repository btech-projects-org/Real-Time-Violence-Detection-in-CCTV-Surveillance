from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "Real_Time_Violence_Detection"
COLLECTION_NAME = "incidents"

client = None
db = None
collection = None

async def init_db():
    global client, db, collection
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Connected to MongoDB at {MONGO_URI}")

async def log_incident(incident_type, confidence, description, image_path):
    if collection is None:
        await init_db()
    
    incident = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": incident_type,
        "confidence": confidence,
        "description": description,
        "image_path": image_path
    }
    await collection.insert_one(incident)
    print(f"Logged incident to MongoDB: {incident_type}")

async def get_incidents(limit=50):
    if collection is None:
        await init_db()
    
    cursor = collection.find().sort("timestamp", -1).limit(limit)
    incidents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"]) # Convert ObjectId to string for JSON serialization
        incidents.append(doc)
    return incidents
