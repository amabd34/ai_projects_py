#!/bin/bash

echo "🎬 Starting AI Movie Discovery Platform..."
echo

# Activate virtual environment and run the application
source venv/Scripts/activate
echo "✅ Virtual environment activated"
echo

echo "🚀 Launching Flask application..."
python src/app.py
