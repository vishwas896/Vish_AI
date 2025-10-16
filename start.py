#!/usr/bin/env python3
"""
Quick Start Script for VISH AI
Run this to start the self-training system locally
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    try:
        import transformers
        import gradio
        import fastapi
        import peft
        print("✅ All dependencies installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("models/vish-ai-mini", exist_ok=True)
    print("✅ Directories created!")

def start_server():
    """Start the VISH AI server"""
    print("\n" + "=" * 60)
    print("🚀 Starting VISH AI Self-Training System")
    print("=" * 60)
    print("\n📍 Access the interface at: http://localhost:7860")
    print("📍 API documentation at: http://localhost:7860/docs")
    print("\n⌨️  Press CTRL+C to stop the server\n")
    print("=" * 60 + "\n")
    
    try:
        subprocess.run([sys.executable, "-m", "app.main"])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down VISH AI...")

def main():
    print("""
    🌟 VISH AI - Self-Training System
    ═══════════════════════════════════
    
    Welcome to the intelligent AI that learns from you!
    """)
    
    if not check_dependencies():
        sys.exit(1)
    
    create_directories()
    start_server()

if __name__ == "__main__":
    main()
