#!/usr/bin/env python3
"""
Simple launcher script for the AI Movie Discovery Platform
This script automatically uses the virtual environment Python
"""

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the virtual environment Python
    venv_python = os.path.join(script_dir, 'venv', 'Scripts', 'python.exe')
    
    # Path to the main application
    app_path = os.path.join(script_dir, 'src', 'app.py')
    
    # Check if virtual environment exists
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv")
        print("Then: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists(app_path):
        print("❌ Application file not found!")
        print(f"Expected: {app_path}")
        sys.exit(1)
    
    print("🎬 Starting AI Movie Discovery Platform...")
    print("✅ Using virtual environment Python")
    print("🚀 Launching Flask application...")
    print()
    
    # Launch the application using the virtual environment Python
    try:
        subprocess.run([venv_python, app_path], cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
