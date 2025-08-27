#!/bin/bash

echo "Deploying Microbehaviour Frontend..."

# Build frontend
echo "Building frontend..."
./build.sh

# Deploy to a simple HTTP server (you can modify this for your hosting provider)
echo "Starting frontend server..."
cd build

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "Starting Python HTTP server..."
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "Starting Python HTTP server..."
    python -m http.server 8000
else
    echo "Python not found. Please install Python to run the frontend server."
    exit 1
fi

echo "Frontend deployed successfully!"
echo "Frontend available at: http://localhost:8000"




