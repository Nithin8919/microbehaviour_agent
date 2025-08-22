#!/bin/bash

# Kill any existing processes on port 5002
lsof -ti:5002 | xargs kill -9 2>/dev/null

# Start the server with proper environment
cd "/Users/nitin/Documents/microbehaviour py"
source .venv/bin/activate
# Load OpenAI API key from .env file
# Create .env file with: echo 'OPENAI_API_KEY=your_key_here' > .env

echo "Starting Microbehaviour Analysis Server on port 5002..."
echo "Frontend will be available at: http://127.0.0.1:5002/"
echo "API endpoint: http://127.0.0.1:5002/analyze"
echo ""

python -m flask --app app/app.py run --host 127.0.0.1 --port 5002 --debug
