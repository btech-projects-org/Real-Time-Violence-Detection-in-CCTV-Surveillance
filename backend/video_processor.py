import cv2
import asyncio
from .detection_engine import detection_engine
from .database import log_incident
import os
from typing import Callable, Dict

class VideoProcessor:
    """
    Hybrid Video Processor
    - Supports parallel processing of weapon and violence detection
    - Maintains frame buffer for CNN-LSTM temporal analysis
    - Optimized for CCTV real-time streaming
    """
    
    def __init__(self, source=0, process_frequency: int = 15):
        """
        Initialize video processor
        
        Args:
            source: Video source (0 for webcam, or file path)
            process_frequency: Process every N-th frame (higher = faster but lower detection frequency)
                              ⚡ Default changed from 90 to 15 for faster response
        """
        self.source = source
        self.cap = None
        self.is_running = False
        self.process_frequency = process_frequency
        self.frame_counter = 0
        self.alert_counter = 0
        
        # ⚡ OPTIMIZATION: Cache for frame processing
        self.last_detection_result = None
        self.last_detection_time = 0
        
    async def start(self, alert_callback: Callable):
        """
        Start video processing
        
        Args:
            alert_callback: Async callback function for alerts
        """
        self.cap = cv2.VideoCapture(self.source)
        self.is_running = True
        
        print(f"📹 [Video Processor] Starting video capture from source: {self.source}")
        print(f"🔄 [Video Processor] Frame processing frequency: 1 per {self.process_frequency} frames")
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ [Video Processor] End of video stream or error reading frame")
                break
            
            self.frame_counter += 1
            
            # Process every N-th frame (balance between detection and performance)
            # This allows CNN-LSTM to accumulate frames while processing periodically
            if self.frame_counter % self.process_frequency == 0:
                result = await detection_engine.analyze_frame(frame)
                
                # Log and alert on detection
                if result.get("detected"):
                    self.alert_counter += 1
                    print(f"🚨 [Alert #{self.alert_counter}] {result.get('type').upper()}: {result.get('description')}")
                    
                    # Save frame for evidence
                    await self._save_alert_evidence(frame, result)
                    
                    # Log to database
                    await self._log_incident(result)
                    
                    # Notify via callback (WebSocket)
                    await alert_callback(self._format_alert_for_client(result))
        
        self.cap.release()
        print("📹 [Video Processor] Video processing stopped")
    
    async def _save_alert_evidence(self, frame, result: Dict):
        """Save frame evidence for alert"""
        try:
            timestamp = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
            img_name = f"alert_{result['type']}_{timestamp}.jpg"
            img_path = os.path.join("alerts", img_name)
            
            if not os.path.exists("alerts"):
                os.makedirs("alerts")
            
            cv2.imwrite(img_path, frame)
            print(f"💾 Evidence saved: {img_path}")
            result["image_path"] = img_path
            
        except Exception as e:
            print(f"❌ Failed to save evidence: {e}")
    
    async def _log_incident(self, result: Dict):
        """Log incident to database"""
        try:
            await log_incident(
                incident_type=result.get("type", "unknown"),
                severity=result.get("severity", "medium"),
                confidence=result.get("confidence", 0.0),
                description=result.get("description", "Unknown incident"),
                image_path=result.get("image_path", ""),
                additional_data=result
            )
        except Exception as e:
            print(f"❌ Failed to log incident: {e}")
    
    def _format_alert_for_client(self, result: Dict) -> Dict:
        """Format alert result for WebSocket client"""
        return {
            "type": result.get("type"),
            "severity": str(result.get("severity", "medium")),
            "confidence": result.get("confidence", 0.0),
            "description": result.get("description", ""),
            "timestamp": self.frame_counter,
            "image_url": f"/alerts/{os.path.basename(result.get('image_path', ''))}",
            "weapon_detected": result.get("weapon_detection", {}).get("detected", False),
            "violence_detected": result.get("violence_detection", {}).get("detected", False),
            "recommended_action": result.get("action", "MONITOR"),
            "system_status": result.get("system_status", {})
        }
    
    def stop(self):
        """Stop video processing"""
        print(f"⏹️  [Video Processor] Stopping... Processed {self.frame_counter} frames, {self.alert_counter} alerts")
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def get_stats(self) -> Dict:
        """Get processor statistics"""
        return {
            "frames_processed": self.frame_counter,
            "alerts_triggered": self.alert_counter,
            "running": self.is_running,
            "source": self.source
        }

video_processor = VideoProcessor()
