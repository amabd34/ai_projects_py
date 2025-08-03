#!/usr/bin/env python3
"""
Movie Search Application Runner
Convenience script to run the application from the project root.
"""

import os
import sys

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Import and run the application
if __name__ == '__main__':
    from app import app
    app.run()
