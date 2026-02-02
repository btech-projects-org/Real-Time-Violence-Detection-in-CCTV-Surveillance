import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)
    db = client["sentinel_ai"]
    collection = db["incidents"]
    
    count = await collection.count_documents({})
    print(f"Incident count in MongoDB: {count}")
    
    cursor = collection.find().sort("timestamp", -1).limit(5)
    async for doc in cursor:
        print(doc)

if __name__ == "__main__":
    asyncio.run(check_db())
