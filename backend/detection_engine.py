import os
from dotenv import load_dotenv
import cv2
import base64
import json
from typing import Dict, Optional

load_dotenv()

# Using local DETR and YOLOv8 models for weapon detection (no cloud API)
try:
    from ultralytics import YOLO
    print("✅ YOLOv8 loaded - Using local weapon detection model")
except ImportError:
    print("⚠️ YOLOv8 not installed - Will download on first use")
    YOLO = None

# Import hybrid detection components
try:
    from .violence_lstm_detector import ViolenceLSTMDetector
    print("✅ CNN-LSTM violence detector available")
    LSTM_AVAILABLE = True
except ImportError:
    print("⚠️ CNN-LSTM not available - weapon detection only")
    LSTM_AVAILABLE = False

try:
    from .model_fusion import DetectionFusionEngine, FUSION_PRESETS
    print("✅ Model fusion engine loaded")
    FUSION_AVAILABLE = True
except ImportError:
    print("⚠️ Model fusion not available")
    FUSION_AVAILABLE = False

from .hybrid_config import get_system_config

class DetectionEngine:
    """
    Hybrid Detection Engine
    Combines weapon detection and violence pattern detection
    Streams:
    - Stream 1: Weapon detection (DETR/YOLOv8) - Frame-level
    - Stream 2: Violence detection (CNN-LSTM) - Sequence-level
    """
    
    def __init__(self, fusion_preset: str = "balanced", enable_violence_detection: bool = False):
        """
        Initialize hybrid detection engine
        
        Args:
            fusion_preset: 'balanced', 'high_security', or 'low_false_positives'
            enable_violence_detection: Enable CNN-LSTM violence detection
                                      DISABLED by default (model is untrained)
        """
        self.config = get_system_config(fusion_preset)
        self.model = None
        self.detector = None
        self.violence_detector = None
        self.fusion_engine = None
        self.last_error = None
        self.enable_violence_detection = enable_violence_detection and LSTM_AVAILABLE
        
        # ⚡ OPTIMIZATION: Frame resizing for faster inference
        self.target_size = (640, 480)  # Reduce from full resolution to 640x480
        self.resize_scale = 1.0
        
        # Initialize weapon detector
        try:
            if YOLO:
                # Load DETR weapon detection model - better for knife detection
                # Using NabilaLM/detr-weapons-detection (more accurate than YOLOv8)
                print("📥 Loading DETR weapon detection model (Stream 1)...")
                from transformers import pipeline
                # ⚡ OPTIMIZATION: Use device_map for GPU efficiency
                self.detector = pipeline("object-detection", model="NabilaLM/detr-weapons-detection", device=0)
                print("✅ DETR weapon detection model loaded successfully")
            else:
                print("⚠️ YOLOv8 not available, install with: pip install ultralytics")
        except Exception as e:
            print(f"❌ Error loading detection model: {e}")
            print("📥 Falling back to YOLOv8...")
            try:
                self.model = YOLO('weights/best.pt')
                # ⚡ OPTIMIZATION: Enable model optimization
                self.model.to('cuda')  # Move to GPU
                print("✅ YOLOv8 loaded as fallback")
                self.detector = None
            except:
                self.last_error = str(e)
        
        # Initialize violence detector (CNN-LSTM)
        if self.enable_violence_detection:
            try:
                print("📥 Loading CNN-LSTM violence detection model (Stream 2)...")
                self.violence_detector = ViolenceLSTMDetector(
                    sequence_length=16,
                    frame_skip=2,
                    confidence_threshold=0.60
                )
                print("✅ CNN-LSTM violence detection model loaded successfully")
            except Exception as e:
                print(f"⚠️ Could not load CNN-LSTM: {e}")
                self.violence_detector = None
                self.enable_violence_detection = False
        

        # Initialize fusion engine
        if FUSION_AVAILABLE and (self.detector or self.model) and self.enable_violence_detection:
            try:
                print("📥 Initializing detection fusion engine...")
                # preset_config = FUSION_PRESETS.get(fusion_preset, FUSION_PRESETS["balanced"])
                self.fusion_engine = DetectionFusionEngine(
                    weapon_threshold=self.config.fusion_config.weapon_threshold,
                    violence_threshold=self.config.fusion_config.violence_threshold,
                    fusion_mode=self.config.fusion_config.fusion_mode
                )
                print(f"✅ Fusion engine loaded ({fusion_preset} preset)")
            except Exception as e:
                print(f"⚠️ Fusion engine failed: {e}")
                self.fusion_engine = None
        
        # Temporal consistency tracking
        self.consecutive_weapon_detections = 0
        self.required_consecutive_frames = 3

    async def analyze_frame(self, frame):
        """
        Hybrid frame analysis combining weapon and violence detection
        
        Stream 1: Weapon Detection (DETR/YOLOv8) - Instant frame-level analysis
        Stream 2: Violence Detection (CNN-LSTM) - Temporal pattern analysis
        Fusion: Combines both streams for comprehensive threat assessment
        """
        
        if not self.model and not self.detector:
            return {
                "detected": False,
                "type": "error",
                "confidence": 0.0,
                "description": "Model not loaded",
                "stream1_weapon": False,
                "stream2_violence": False,
                "error": True
            }
        
        try:
            # STREAM 1: Weapon Detection (Frame-level)
            weapon_result = await self._detect_weapons(frame)
            
            # Temporal Consistency Check
            if weapon_result.get("detected"):
                self.consecutive_weapon_detections += 1
                if self.consecutive_weapon_detections < self.required_consecutive_frames:
                    print(f"⏳ Potential threat tracking: {self.consecutive_weapon_detections}/{self.required_consecutive_frames} frames")
                    # Downgrade to normal/investigating until persistence is met
                    weapon_result = {
                        "detected": False,
                        "type": "validating",
                        "confidence": weapon_result.get("confidence"),
                        "description": f"Verifying threat ({self.consecutive_weapon_detections}/{self.required_consecutive_frames})...",
                        "model": weapon_result.get("model")
                    }
            else:
                self.consecutive_weapon_detections = 0
            
            # STREAM 2: Violence Detection (Temporal pattern)
            violence_result = {}
            if self.enable_violence_detection and self.violence_detector:
                violence_result = self.violence_detector.add_frame(frame)
            else:
                violence_result = {"detected": False, "confidence": 0.0, "type": "none"}
            
            # FUSION: Combine both streams
            if self.fusion_engine:
                fused_result = self.fusion_engine.fuse_detections(weapon_result, violence_result)
                # Add system status information
                fused_result["system_status"] = self.fusion_engine.get_system_status()
                fused_result["trend"] = self.fusion_engine.get_trend_analysis()
                return fused_result
            else:
                # Fallback: Return weapon detection if no fusion
                return weapon_result
            
        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Error in hybrid detection: {error_message}")
            import traceback
            traceback.print_exc()
            
            self.last_error = error_message
            return {
                "detected": False,
                "type": "error",
                "confidence": 0.0,
                "description": f"Hybrid detection error: {str(e)}",
                "stream1_weapon": False,
                "stream2_violence": False,
                "error": True
            }
    
    async def _detect_weapons(self, frame) -> Dict:
        """
        STREAM 1: Weapon Detection
        Frame-level object detection for weapons
        ⚡ OPTIMIZED: Resize frame for faster inference while maintaining accuracy
        """
        print("🔍 [Stream 1] Analyzing frame for weapons...")
        
        # Get configured thresholds
        detr_threshold = self.config.weapon_config.detr_confidence_threshold
        yolo_threshold = self.config.weapon_config.yolo_confidence_threshold
        
        try:
            # ⚡ OPTIMIZATION: Resize frame for faster inference
            original_height, original_width = frame.shape[:2]
            target_width, target_height = self.target_size
            
            # Calculate resize scale for bbox adjustment
            self.resize_scale = target_width / original_width
            
            # Resize frame for faster processing
            resized_frame = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)
            
            # Try DETR first (better for knives)
            if hasattr(self, 'detector') and self.detector and self.config.weapon_config.detr_enabled:
                try:
                    from PIL import Image
                    import time
                    
                    # Convert BGR to RGB for PIL
                    frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    
                    start_time = time.time()
                    # Using configured threshold
                    detections = self.detector(image, threshold=detr_threshold)
                    inference_time = time.time() - start_time
                    print(f"📊 [Stream 1] DETR Detections: {len(detections)} (inference: {inference_time:.2f}s)")
                    
                    if detections:
                        # Filter by configured threshold
                        valid_detections = [d for d in detections if d['score'] >= detr_threshold]
                        
                        if valid_detections:
                            top_detection = max(valid_detections, key=lambda x: x['score'])
                            confidence = top_detection['score']
                            weapon_type = top_detection['label']
                            bbox = top_detection.get('box', {})
                            
                            # FIX: Additional validation - check bounding box size
                            # Small detections are often false positives
                            if bbox:
                                width = bbox.get('xmax', 0) - bbox.get('xmin', 0)
                                height = bbox.get('ymax', 0) - bbox.get('ymin', 0)
                                area = width * height
                                
                                # Reject very small detections (likely false positives)
                                # Increased from 500 to 2000 to filter out small noise
                                if area < 2000:
                                    print(f"⚠️ [Stream 1] Detection too small (area: {area:.0f}), ignoring")
                                    # Continue to YOLO fallback instead of raising error?
                                    # raise ValueError("Detection area too small")
                                    pass
                                else:

                                    weapon_map = {
                                        'LABEL_0': 'knife', 'LABEL_1': 'pistol',
                                        'LABEL_2': 'rifle', 'LABEL_3': 'knife',
                                        'knife': 'knife', 'pistol': 'pistol',
                                        'gun': 'pistol', 'rifle': 'rifle'
                                    }
                                    
                                    clean_weapon = weapon_map.get(weapon_type.lower(), weapon_type)
                                    
                                    # Only reject if the label wasn't in the weapon_map (truly unmapped)
                                    if weapon_type.lower() not in weapon_map:
                                        print(f"⚠️ [Stream 1] Unknown label {weapon_type}, might be false positive")
                                        # Still allow it, just mark as 'unknown weapon'
                                        clean_weapon = 'unknown weapon'
                                    
                                    confidence_percent = round(float(confidence) * 100)
                                    
                                    print(f"🚨 [Stream 1] WEAPON ALERT: {clean_weapon} ({confidence_percent}%)")
                                    
                                    return {
                                        "detected": True,
                                        "type": "weapon",
                                        "weapon_type": clean_weapon,
                                        "confidence": round(float(confidence), 3),
                                        "description": f"⚠️ Weapon detected: {clean_weapon} ({confidence_percent}%)",
                                        "model": "DETR"
                                    }
                except Exception as e:
                    print(f"⚠️ [Stream 1] DETR failed: {e}")
            
            # Fallback to YOLOv8
            if self.model and self.config.weapon_config.yolo_enabled:
                # ⚡ OPTIMIZATION: Use resized frame and imgsz parameter for faster inference
                import time
                start_time = time.time()
                # Using configured threshold
                results = self.model(resized_frame, conf=yolo_threshold, verbose=False, imgsz=640)
                inference_time = time.time() - start_time
                detections = results[0]
                print(f"📊 [Stream 1] YOLOv8 Detections: {len(detections.boxes)} (inference: {inference_time:.2f}s)")
                
                if len(detections.boxes) > 0:
                    valid_detections = []
                    for box in detections.boxes:
                        conf = float(box.conf[0])
                        # Filter by configured threshold
                        if conf >= yolo_threshold:
                            class_id = int(box.cls[0])
                            class_name = detections.names[class_id]
                            valid_detections.append({'class': class_name, 'confidence': conf})
                    
                    if valid_detections:
                        top_weapon = max(valid_detections, key=lambda x: x['confidence'])
                        confidence = top_weapon['confidence']
                        weapon_type = top_weapon['class']
                        confidence_percent = round(float(confidence) * 100)
                        
                        print(f"🚨 [Stream 1] WEAPON ALERT: {weapon_type} ({confidence_percent}%)")
                        
                        return {
                            "detected": True,
                            "type": "weapon",
                            "weapon_type": weapon_type,
                            "confidence": round(confidence, 3),
                            "description": f"⚠️ Weapon detected: {weapon_type} ({confidence_percent}%)",
                            "model": "YOLOv8"
                        }
            
            print("✅ [Stream 1] No weapons detected")
            return {
                "detected": False,
                "type": "normal",
                "confidence": 0.0,
                "description": "No weapons detected",
                "model": "DETR/YOLOv8"
            }
            
        except Exception as e:
            print(f"❌ [Stream 1] Weapon detection error: {e}")
            return {
                "detected": False,
                "type": "error",
                "confidence": 0.0,
                "description": f"Weapon detection error: {str(e)}"
            }
    
    def get_detector_status(self) -> Dict:
        """Get current status of all detectors"""
        status = {
            "weapon_detector": "active" if (self.detector or self.model) else "inactive",
            "violence_detector": "active" if self.enable_violence_detection and self.violence_detector else "inactive",
            "fusion_engine": "active" if self.fusion_engine else "inactive",
            "detection_mode": "hybrid" if self.fusion_engine else "weapon_only",
            "thresholds": {
                "detr": self.config.weapon_config.detr_confidence_threshold,
                "yolo": self.config.weapon_config.yolo_confidence_threshold
            }
        }
        
        if self.violence_detector:
            status["buffer_stats"] = self.violence_detector.get_buffer_stats()
        
        if self.fusion_engine:
            status["system_status"] = self.fusion_engine.get_system_status()
        
        return status


# Initialize hybrid detection engine
# IMPORTANT: Violence detection disabled by default (untrained model)
# Weapon detection (DETR/YOLOv8) remains active
# FIX: Using 'low_false_positives' preset to prevent false notifications
detection_engine = DetectionEngine(fusion_preset="low_false_positives", enable_violence_detection=False)

