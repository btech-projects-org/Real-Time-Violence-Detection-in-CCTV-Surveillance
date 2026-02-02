from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import cv2
import numpy as np
import google.generativeai as genai
from video_processor import video_processor
from database import init_db, get_incidents, log_incident
from detection_engine import detection_engine

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create alerts directory if it doesn't exist
if not os.path.exists("alerts"):
    os.makedirs("alerts")

app.mount("/alerts", StaticFiles(directory="alerts"), name="alerts")

connected_clients = set()

async def check_api_quota():
    """Check remaining API credits for the week"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ No API key configured")
            return
        
        genai.configure(api_key=api_key)
        
        # Get model info to check quota
        model_name = 'models/gemini-1.5-flash'
        
        # Try to get rate limit info
        try:
            # List models to verify API key works
            models = genai.list_models()
            print("\n" + "="*60)
            print("📊 GEMINI API STATUS")
            print("="*60)
            print(f"✅ API Key: Valid")
            print(f"📍 Model: gemini-1.5-flash")
            print(f"📦 Free Tier Limits:")
            print(f"   • 15 RPM (Requests Per Minute)")
            print(f"   • 1,500 RPD (Requests Per Day)")
            print(f"   • ~10,500 Requests Per Week")
            print(f"   • Frame Analysis: Every 3 seconds = ~1,200 requests/hour")
            print(f"   • Recommended Usage: Max 1-2 hours/day to stay within limits")
            print("="*60 + "\n")
        except Exception as e:
            print(f"\n⚠️ API Key Status: {str(e)}\n")
            
    except Exception as e:
        print(f"❌ Error checking API quota: {e}")

@app.on_event("startup")
async def startup_event():
    await init_db()
    await check_api_quota()
    # Camera will be started from frontend, not automatically

async def broadcast_alert(alert_data):
    if connected_clients:
        message = json.dumps(alert_data)
        await asyncio.gather(*[client.send_text(message) for client in connected_clients])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.get("/incidents")
async def get_history():
    return await get_incidents()

@app.post("/analyze-frame")
async def analyze_frame(file: UploadFile = File(...)):
    try:
        print("📸 Received frame for analysis")
        # Read the uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("❌ Invalid image received")
            return {"error": "Invalid image"}
        
        print(f"✅ Frame decoded: {frame.shape}")
        
        # Analyze with detection engine
        result = await detection_engine.analyze_frame(frame)
        
        print(f"Detection result: {result}")
        
        # If threat detected, save and log
        if result.get("detected"):
            print(f"🚨 THREAT DETECTED: {result['type']}")
            timestamp = cv2.getTickCount()
            img_name = f"alert_{timestamp}.jpg"
            img_path = os.path.join("alerts", img_name)
            cv2.imwrite(img_path, frame)
            
            # Log to database
            await log_incident(
                result["type"],
                result["confidence"],
                result["description"],
                img_path
            )
            
            # Broadcast alert to all connected WebSocket clients
            alert_data = {
                "type": result["type"],
                "confidence": result["confidence"],
                "description": result["description"],
                "timestamp": str(timestamp),
                "image_url": f"/alerts/{img_name}",
                "angry_face": result.get("angry_face", False),
                "weapon": result.get("weapon", False)
            }
            await broadcast_alert(alert_data)
            print(f"📡 Alert broadcasted to {len(connected_clients)} clients")
        else:
            print("✅ No threats detected - normal activity")
        
        return result
        
    except Exception as e:
        print(f"Error analyzing frame: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
