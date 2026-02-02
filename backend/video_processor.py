import cv2
import asyncio
from detection_engine import detection_engine
from database import log_incident
import os

class VideoProcessor:
    def __init__(self, source=0):
        self.source = source
        self.cap = None
        self.is_running = False

    async def start(self, alert_callback):
        self.cap = cv2.VideoCapture(self.source)
        self.is_running = True
        
        frame_count = 0
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Process every 90th frame (approx every 3 seconds) to stay under 20 RPM limit
            if frame_count % 90 == 0:
                result = await detection_engine.analyze_frame(frame)
                if result.get("detected"):
                    # Save frame for evidence
                    timestamp = cv2.getTickCount()
                    img_name = f"alert_{timestamp}.jpg"
                    img_path = os.path.join("alerts", img_name)
                    if not os.path.exists("alerts"):
                        os.makedirs("alerts")
                    cv2.imwrite(img_path, frame)
                    
                    # Log to DB
                    await log_incident(
                        result["type"], 
                        result["confidence"], 
                        result["description"], 
                        img_path
                    )
                    
                    # Notify via callback (WebSocket)
                    await alert_callback({
                        "type": result["type"],
                        "confidence": result["confidence"],
                        "description": result["description"],
                        "timestamp": timestamp,
                        "image_url": f"/alerts/{img_name}"
                    })

            frame_count += 1
            await asyncio.sleep(0.01) # Small sleep to yield control

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()

video_processor = VideoProcessor()
