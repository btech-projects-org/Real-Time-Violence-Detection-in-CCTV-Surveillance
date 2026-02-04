# -*- coding: utf-8 -*-
"""
# 🔍 Violence Detection System – Full Evaluation Notebook
Built for Google Colab & Local Development | Enhanced Reliability & Object detection

This script performs a complete evaluation of the hybrid Violence Detection System.
Compatible with Google Colab and local environments.
"""

import os
import sys
import cv2
import time
import torch
import warnings
import requests
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from collections import Counter

# ==========================================
# STEP 1: ENVIRONMENT DETECTION & CONFIG
# ==========================================

# Detect if running in Google Colab
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# Suppress Noise (Warnings & Logs)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["PYTHONWARNINGS"] = "ignore"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"System: Running on {DEVICE.upper()} (Colab: {IN_COLAB})")

# Visualization settings
if IN_COLAB:
    try:
        from google.colab.patches import cv2_imshow
        DISPLAY_FUNC = cv2_imshow
    except ImportError:
        DISPLAY_FUNC = None
else:
    def DISPLAY_FUNC(img):
        plt.figure(figsize=(10, 6))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

# ==========================================
# STEP 2: MODEL INITIALIZATION
# ==========================================

# Add project root to path if local
if not IN_COLAB:
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    sys.path.append(os.path.join(project_root, "backend"))

detection_engine = None
yolo_model = None
detr_processor = None
detr_model = None

try:
    if not IN_COLAB:
        from backend.detection_engine import detection_engine
        print("✅ Using project's DetectionEngine")
except ImportError:
    print("⚠️ Backend DetectionEngine not found. Falling back to standalone loading.")

if not detection_engine:
    # Standalone loading for Colab or if backend is missing
    from ultralytics import YOLO
    from transformers import DetrImageProcessor, DetrForObjectDetection
    
    # 2.1 Load DETR (Primary Weapon Detection)
    print("Loading DETR model (Primary)...")
    detr_processor = DetrImageProcessor.from_pretrained("NabilaLM/detr-weapons-detection")
    detr_model = DetrForObjectDetection.from_pretrained(
        "NabilaLM/detr-weapons-detection"
    ).to(DEVICE)
    detr_model.eval()

    # 2.2 Load YOLOv8 (Fallback Weapon Detection)
    print("Loading YOLOv8 model (Fallback)...")
    YOLO_WEIGHTS_PATH = "/content/weights/best.pt" if IN_COLAB else os.path.join("backend", "weights", "best.pt")
    
    if os.path.exists(YOLO_WEIGHTS_PATH):
        yolo_model = YOLO(YOLO_WEIGHTS_PATH)
    else:
        print(f"Custom weights not found at {YOLO_WEIGHTS_PATH}. Falling back to yolov8n.pt")
        yolo_model = YOLO("yolov8n.pt")

# ==========================================
# STEP 3: CORE UTILITIES
# ==========================================

def download_file(url, local_path):
    """Robust download utility."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=15)
        if response.status_code != 200:
            return False
            
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def run_evaluation_inference(image_path, conf_threshold=0.75):
    """Abstraction layer for inference using either DetectionEngine or standalone models."""
    if not os.path.exists(image_path):
        return {"model": "None", "detections": 0, "status": "Missing"}

    img = cv2.imread(image_path)
    if img is None:
        return {"model": "None", "detections": 0, "status": "Corrupted"}

    if detection_engine:
        # Wrap the async call
        import asyncio
        res = asyncio.run(detection_engine.analyze_frame(img))
        return {
            "model": "DetectionEngine",
            "detections": 1 if res["detected"] else 0,
            "status": "OK"
        }
    else:
        # Standalone logic
        # 1. DETR
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        inputs = detr_processor(images=image_rgb, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = detr_model(**inputs)
        results = detr_processor.post_process_object_detection(
            outputs, threshold=conf_threshold, target_sizes=[image_rgb.shape[:2]]
        )[0]

        if len(results["scores"]) > 0:
            return {"model": "DETR", "detections": len(results["scores"]), "status": "OK"}
        
        # 2. YOLO Fallback
        yolo_res = yolo_model(image_path, conf=conf_threshold, verbose=False)[0]
        return {"model": "YOLO", "detections": len(yolo_res.boxes), "status": "OK"}

def evaluate_video(video_path, frame_skip=15):
    """Processes video for evaluation."""
    if not os.path.exists(video_path): return 0, 0
    cap = cv2.VideoCapture(video_path)
    frames_checked = 0
    detections = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frames_checked += 1
        if frames_checked % frame_skip != 0: continue
        
        cv2.imwrite("temp_eval.jpg", frame)
        res = run_evaluation_inference("temp_eval.jpg")
        if res["detections"] > 0:
            detections += 1
    cap.release()
    if os.path.exists("temp_eval.jpg"): os.remove("temp_eval.jpg")
    return detections, frames_checked

# ==========================================
# STEP 4: DATA SETUP
# ==========================================

test_data = {
    "images": {
        "Weapon (Gun)": ("https://raw.githubusercontent.com/jsh-89/Weapon-Detection/master/test_images/gun1.jpg", "test_images/gun.jpg"),
        "Weapon (Knife)": ("https://raw.githubusercontent.com/jsh-89/Weapon-Detection/master/test_images/knife1.jpg", "test_images/knife.jpg"),
        "Neutral (Bus)": ("https://github.com/ultralytics/yolov5/raw/master/data/images/bus.jpg", "test_images/no_weapon.jpg"),
    },
    "videos": {
        "Activity (Station)": ("https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4", "test_videos/activity.mp4"),
        "Neutral (Walking)": ("https://github.com/intel-iot-devkit/sample-videos/raw/master/face-demographics-walking-and-pause.mp4", "test_videos/normal.mp4"),
    }
}

def setup_assets():
    print("Downloading test assets...")
    for category, items in test_data.items():
        for label, (url, path) in items.items():
            if not os.path.exists(path):
                download_file(url, path)

# ==========================================
# STEP 5: EXECUTION
# ==========================================

def run_full_evaluation():
    setup_assets()
    evaluation_log = {"image_tests": [], "video_tests": []}

    print("\n--- Starting Image Tests ---")
    for label, (url, path) in test_data["images"].items():
        if not os.path.exists(path): continue
        start_time = time.time()
        res = run_evaluation_inference(path)
        latency = time.time() - start_time
        evaluation_log["image_tests"].append({
            "test": label, "model": res["model"], "detected": res["detections"] > 0, 
            "latency": round(latency, 3), "status": res["status"]
        })

    print("\n--- Starting Video Tests ---")
    for label, (url, path) in test_data["videos"].items():
        if not os.path.exists(path): continue
        hits, total = evaluate_video(path)
        evaluation_log["video_tests"].append({
            "video": label, "detections": hits, "total_frames": total,
            "rate": round(hits/total, 3) if total > 0 else 0
        })

    print("\n================= EVALUATION SUMMARY REPORT =================\n")
    print("▶ Image Evaluation")
    for test in evaluation_log["image_tests"]:
        status = "✅ DETECTED" if test["detected"] else "❌ NO DETECTION"
        print(f"   - {test['test']}: {status} (via {test['model']}, {test['latency']}s)")

    print("\n▶ Video Evaluation")
    for test in evaluation_log["video_tests"]:
        print(f"   - {test['video']}: {test['detections']} alerts (Rate: {test['rate']})")

if __name__ == "__main__":
    # If in Colab, user might want to run cells manually.
    # But for a script or 'Run All', this works perfectly.
    run_full_evaluation()