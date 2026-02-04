# Real-Time Violence Detection in CCTV Surveillance

**An Advanced Hybrid Threat Detection System** leveraging **Dual-Stream AI (Spatial + Temporal)** to detect weapons and violence in real-time.

![Status](https://img.shields.io/badge/Status-Operational-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React_19-61DAFB)
![Deep Learning](https://img.shields.io/badge/AI-YOLOv8_%7C_DETR_%7C_CNN--LSTM-FF6F00)

## 🚀 Features

*   **Dual-Stream Hybrid Detection**: simultaneously processes spatial features (weapons) and temporal features (violent actions) to minimize false positives.
    *   **Stream 1 (Spatial)**: Detects **Guns, Knives, Rifles** using **DETR (DEtection TRansformer)** and **YOLOv8**.
    *   **Stream 2 (Temporal)**: Detects **Fighting, Punching, Kicking** using **CNN-LSTM** (Long Short-Term Memory) networks.
*   **Fusion Engine**: Intelligent logic that correlates object data with motion data for high-confidence alerts.
*   **Real-Time Dashboard**: React-based command center with live video streaming and instantaneous alert feeds via WebSockets.
*   **Evidence Logging**: Automatically captures and stores high-resolution snapshots of detected threats to a secure local directory (`alerts/`) and MongoDB.
*   **Edge-Ready**: Optimized for performance on standard hardware with CUDA acceleration support.

## 🛠️ Tech Stack

*   **Frontend**: React 19, Vite 7, TailwindCSS 4, WebSockets.
*   **Backend**: Python 3.10+, FastAPI, Uvicorn (ASGI).
*   **Deep Learning**: 
    *   **Object Detection**: `transformers` (Hugging Face DETR), `ultralytics` (YOLOv8).
    *   **Action Recognition**: `torch` (PyTorch CNN-LSTM).
    *   **Vision**: OpenCV (cv2), Pillow.
*   **Database**: MongoDB (Async Motor driver).
*   **Automation**: PowerShell Automation Scripts.

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Real-Time Violence Detection in CCTV Surveillance"
```

### 2. Environment Setup
We adhere to **12-Factor App principles**. Create a `.env` file in the root directory:

```ini
# .env content
MONGO_URI=mongodb://localhost:27017
```

### 3. Automated Setup (Recommended)
We provide a **one-click setup script** that handles virtual environments, dependencies, and server startup.

**For Windows (PowerShell):**
```powershell
# Installs dependencies and starts BOTH Backend and Frontend
.\start-all.ps1
```

### 4. Manual Setup
If you prefer manual configuration:

**Backend:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python backend/run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🛡️ Usage

1.  **Access the Monitor**: Open `http://localhost:5173` in your browser.
2.  **Live Analysis**: The system will immediately connect to the video feed (default: configured camera/file) and begin the **Dual-Stream Analysis**.
3.  **Alerts**:
    *   **Visual**: The dashboard border flashes RED.
    *   **Log**: The incident is recorded in the "Recent Alerts" panel.
    *   **Storage**: A snapshot is saved to `alerts/` and logged to MongoDB.

## 📘 System Architecture & Documentation

### 1. Project Overview
This system is designed for high-security environments where passive recording is insufficient. Unlike standard CCTV, this project bridges the gap between surveillance and intervention by making **instantaneous decisions**.

The core innovation is the **Hybrid Fusion Architecture**:
*   A person holding a phone (Object) might look like a gun locally.
*   A person waving hello (Motion) might look like a punch locally.
*   **Fusion**: The system only alerts if it sees *Threat Objects* AND/OR *Aggressive Motion* patterns, cross-referencing them to rule out benign activities.

### 2. Repository Structure

```
Real-Time Violence Detection/
│
├── backend/                       # 🧠 Core Python Backend & AI Engine
│   ├── detection_engine.py        # MAIN AI ENGINE: Orchestrates DETR, YOLO, and LSTM
│   ├── video_processor.py         # High-performance threading for video capture
│   ├── violence_lstm_detector.py  # Temporal Action Recognition (Stream 2)
│   ├── model_fusion.py            # Logic to combine/weight scores from both streams
│   ├── main.py                    # FastAPI Entry & WebSocket Controller
│   ├── database.py                # MongoDB Persistence Layer
│   └── weights/                   # Local storage for AI Models
│
├── frontend/                      # 🎨 React Frontend
│   ├── src/                       # UI Components & Contexts
│   └── vite.config.js             # Build Config
│
├── alerts/                        # 📸 Evidence Locker (Auto-generated snapshots)
├── test_videos/                   # 🎞️ Standardized datasets for validation
├── start-all.ps1                  # ⚡ Production Entry Point Script
├── requirements.txt               # 📦 Precise Dependency Graph
└── README.md                      # 📄 System Documentation
```

### 3. Dependency Analysis

The `requirements.txt` defines a precise ML runtime:

*   **Core API**: `fastapi`, `uvicorn` (Async I/O for real-time non-blocking alerts).
*   **Computer Vision**:
    *   `ultralytics`: Industry-standard YOLOv8 for fast edge detection.
    *   `transformers`: Hugging Face implementation of DETR (End-to-End Object Detection).
    *   `timm`, `torch`: PyTorch backend for the LSTM temporal model.
*   **Infrastructure**: `motor` (Async MongoDB), `python-dotenv`.

### 4. Application Execution Flow

1.  **Bootstrapping**: `start-all.ps1` verifies Python/Node environments.
2.  **Initialization**:
    *   `main.py` wakes up.
    *   `DetectionEngine` loads models into VRAM (DETR + YOLO + LSTM).
    *   Database connection established via `database.py`.
3.  **Runtime Loop (Per Frame)**:
    *   **Input**: Frame captured by `video_processor`.
    *   **Stream 1**: DETR scans for weapons.
    *   **Stream 2**: Frame added to a 16-frame buffer for LSTM analysis.
    *   **Fusion**: Scores combined. IF `Threat_Score > Threshold`:
        *   Snapshot Saved.
        *   Details Logged to DB.
        *   JSON Payload broadcast via WebSocket.
    *   **Output**: React Frontend renders the bounding boxes and alerts.

### 5. System Requirements

**Minimum Requirements (CPU Mode)**:
*   **OS**: Windows 10/11 / Linux.
*   **CPU**: Intel Core i5 (8th Gen) or newer.
*   **RAM**: 8 GB (AI models require significant memory).
*   **Python**: 3.8 - 3.11.

**Recommended (GPU Accelerated)**:
*   **GPU**: NVIDIA GTX 1660 / RTX 3050 or better.
*   **CUDA**: 11.8+ installed.
*   **Performance**: ~15-30 FPS on GPU (vs 2-5 FPS on CPU).

## 📄 License

MIT License. Open for educational and security research usage.
