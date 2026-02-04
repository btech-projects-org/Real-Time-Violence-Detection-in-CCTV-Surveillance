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
from .video_processor import video_processor
from .database import init_db, get_incidents, log_incident
from .detection_engine import detection_engine
from .hybrid_config import get_system_config
import time

# Load hybrid system configuration
SYSTEM_CONFIG = get_system_config("low_false_positives")  # Can be 'balanced', 'high_security', 'low_false_positives'

# ⚡ OPTIMIZATION: Result caching to avoid duplicate processing
last_frame_hash = None
last_result = None
last_result_time = 0
CACHE_DURATION = 0.1  # Cache for 100ms to avoid redundant processing

app = FastAPI(
    title="Real-Time Violence Detection System",
    description="Hybrid weapon + behavioral violence detection",
    version="2.0"
)

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

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    await init_db()
    
    print("\n" + "="*70)
    print("🚀 REAL-TIME SURVEILLANCE SYSTEM - STARTING UP")
    print("="*70)
    
    # Print configuration
    SYSTEM_CONFIG.print_config()
    
    print("✅ Backend Initialized")
    print("✅ Weapon Detection: ACTIVE (Stream 1)")
    print("✅ Violence Detection: ACTIVE (Stream 2)" if SYSTEM_CONFIG.violence_config.enabled else "⚠️  Violence Detection: DISABLED")
    print("✅ Detection Fusion: ACTIVE")
    print("\n📡 WebSocket server ready at: ws://localhost:8000/ws")
    print("🎥 Ready to receive video streams\n")


async def broadcast_alert(alert_data):
    """Broadcast alert to all connected WebSocket clients"""
    if connected_clients:
        message = json.dumps(alert_data)
        await asyncio.gather(*[client.send_text(message) for client in connected_clients], return_exceptions=True)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"🔗 WebSocket client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            # Receive and ignore client messages (keep connection alive)
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"🔌 WebSocket client disconnected. Total clients: {len(connected_clients)}")


@app.get("/status")
async def system_status():
    """Get current system status"""
    detector_status = detection_engine.get_detector_status()
    video_stats = video_processor.get_stats()
    
    return {
        "system": "HYBRID_SURVEILLANCE",
        "status": "operational",
        "detection_mode": "Weapon + Behavioral Violence",
        "configuration": SYSTEM_CONFIG.preset,
        "detector_status": detector_status,
        "video_processor": video_stats,
        "connected_clients": len(connected_clients),
        "system_config": SYSTEM_CONFIG.get_full_config()
    }


@app.get("/incidents")
async def get_history():
    """Get incident history from database"""
    return await get_incidents()

@app.post("/analyze-frame")
async def analyze_frame(file: UploadFile = File(...)):
    """Analyze a single frame for threats"""
    global last_frame_hash, last_result, last_result_time
    
    try:
        print("📸 Received frame for hybrid analysis")
        # Read the uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        
        # ⚡ OPTIMIZATION: Hash frame to detect duplicates
        import hashlib
        frame_hash = hashlib.md5(nparr).hexdigest()
        
        # Return cached result if same frame received recently
        current_time = time.time()
        if frame_hash == last_frame_hash and (current_time - last_result_time) < CACHE_DURATION:
            print(f"⚡ [CACHE HIT] Returning cached result (age: {(current_time - last_result_time)*1000:.0f}ms)")
            return last_result
        
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("❌ Invalid image received")
            return {"error": "Invalid image"}
        
        print(f"✅ Frame decoded: {frame.shape}")
        
        # Analyze with hybrid detection engine
        # Increment stats so UI shows activity
        video_processor.frame_counter += 1
        result = await detection_engine.analyze_frame(frame)
        
        # ⚡ OPTIMIZATION: Cache result
        last_frame_hash = frame_hash
        last_result = result
        last_result_time = current_time
        
        print(f"Detection result: {result}")

        # If analysis failed, return error to frontend without logging incidents
        if result.get("error") or result.get("type") == "error":
            print("⚠️ Analysis error returned to client")
            return result
        
        # If threat detected, save and log
        if result.get("detected"):
            video_processor.alert_counter += 1
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
