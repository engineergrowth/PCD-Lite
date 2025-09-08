#!/usr/bin/env python3
"""
PCD-Lite Demo Startup Script
Starts both the FastAPI server and Streamlit dashboard
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def start_fastapi():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI server...")
    os.chdir(Path(__file__).parent)
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])

def start_streamlit():
    """Start Streamlit dashboard"""
    print("📊 Starting Streamlit dashboard...")
    time.sleep(3)  # Wait for FastAPI to start
    os.chdir(Path(__file__).parent)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])

def main():
    """Main startup function"""
    print("🎬 PCD-Lite Demo Startup")
    print("=" * 40)
    print("Starting both FastAPI server and Streamlit dashboard...")
    print("")
    print("📡 FastAPI will be available at: http://localhost:8000")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("")
    print("Press Ctrl+C to stop both services")
    print("=" * 40)
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Streamlit in the main thread
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down PCD-Lite demo...")
        sys.exit(0)

if __name__ == "__main__":
    main()
