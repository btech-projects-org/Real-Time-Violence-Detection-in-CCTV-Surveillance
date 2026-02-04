#!/usr/bin/env python3
"""
Direct backend runner
This file allows running: python main.py from the backend directory
"""

import sys
import os

# Ensure project root is on sys.path so package imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now run the app
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Real-Time Violence Detection Backend...")
    print("📡 Server running at: http://0.0.0.0:8000")
    print("📚 API Docs: http://localhost:8000/docs")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=project_root
    )
