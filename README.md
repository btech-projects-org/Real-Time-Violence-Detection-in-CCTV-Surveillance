# Real-Time Violence Detection in CCTV Surveillance

A real-time AI-powered violence detection system using CCTV surveillance footage.

## 🏗️ Project Structure

```
.
├── backend/                 # FastAPI backend server
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── detection_engine.py # AI detection logic using Gemini
│   ├── video_processor.py  # Video frame processing
│   └── database.py         # MongoDB integration
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── alerts/                 # Stored alert images
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 📋 Prerequisites

- Python 3.12+ with virtual environment (.venv)
- Node.js 20.16.0+ and npm
- MongoDB (local or Atlas cloud)
- Google Gemini API key (optional - runs in DEMO mode without it)

## 🔧 Installation

### 1. Python Backend Setup

All Python dependencies are already installed in the virtual environment (`.venv`):

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify installation
pip list
```

**Installed packages:**
- fastapi==0.115.6
- uvicorn==0.34.0
- motor==3.6.0
- pymongo>=4.9,<4.10
- opencv-python==4.10.0.84
- google-generativeai==0.8.3
- python-dotenv==1.0.1
- websockets==14.1
- aiofiles==24.1.0
- python-multipart==0.0.20

### 2. Frontend Setup

All Node.js dependencies are already installed:

```powershell
cd frontend
npm install  # Already done, just verifying
```

**Key dependencies:**
- React 19.2.0
- Vite 7.2.4
- Tailwind CSS 4.1.18

### 3. Environment Configuration

Create/edit `.env` file in the root directory:

```env
# Google Gemini API (optional - runs in DEMO mode without it)
GEMINI_API_KEY=your_api_key_here

# MongoDB Connection
MONGO_URI=mongodb://localhost:27017
```

## 🚀 Running the Application

### Option 1: Using PowerShell Scripts (Recommended)

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws

## 📊 Features

✅ Real-time CCTV video processing
✅ AI-powered violence detection using Google Gemini
✅ WebSocket live alerts
✅ MongoDB incident logging
✅ React dashboard with live feed
✅ Historical incident tracking
✅ Alert image storage

## 🔍 API Endpoints

- `GET /incidents` - Retrieve incident history
- `WebSocket /ws` - Real-time alert streaming

## 🛠️ Development

### Backend Development
- Runs on port 8000 with auto-reload
- Uses FastAPI framework
- MongoDB for data persistence
- DEMO mode when Gemini API key is invalid/missing

### Frontend Development
- Runs on port 5173 with hot module reload
- React 19 with hooks
- Tailwind CSS for styling
- WebSocket for real-time updates

## 📝 Notes

- System currently runs in **DEMO MODE** (simulated alerts)
- To enable real AI detection, add a valid `GEMINI_API_KEY` in `.env`
- MongoDB connection defaults to `mongodb://localhost:27017`
- Ensure MongoDB is running before starting the backend
- Alert images are stored in the `alerts/` directory

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Check if port 8000 is available
- Verify MongoDB is running

**Frontend won't start:**
- Check if port 5173 is available
- Run `npm install` in frontend directory
- Ensure Node.js version is 20.16.0+

**WebSocket connection fails:**
- Ensure backend is running first
- Check CORS settings in `backend/main.py`
- Verify firewall allows WebSocket connections

## 📦 Package Management

**Add Python package:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install package-name
pip freeze > requirements.txt
```

**Add npm package:**
```powershell
cd frontend
npm install package-name
```

## 🔐 Security

- Keep `.env` file private
- Never commit API keys to version control
- Use `.env.example` for sharing configuration templates

## 📄 License

This project is for educational and demonstration purposes.
