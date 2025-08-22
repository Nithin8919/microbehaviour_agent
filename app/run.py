#!/usr/bin/env python3
"""
Startup script for the Microbehavior Analyzer Flask application.
This script ensures proper environment setup and starts the Flask server.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import microbehaviour modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Check if .env file exists
env_file = parent_dir / '.env'
if not env_file.exists():
    print("⚠️  Warning: .env file not found!")
    print("Please create a .env file with your OpenAI API key:")
    print("echo 'OPENAI_API_KEY=your_api_key_here' > .env")
    print()

# Import and run the Flask app
try:
    from app import app
    print("🚀 Starting Microbehavior Analyzer...")
    print("📍 URL: http://localhost:5000")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
    
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
