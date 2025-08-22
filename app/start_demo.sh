#!/bin/bash

# Start the Microbehavior Analyzer Demo
echo "🚀 Starting Microbehavior Analyzer Demo..."
echo "📍 URL: http://localhost:5001"
echo "🔄 Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
source ../.venv/bin/activate
python demo.py
