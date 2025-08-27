#!/bin/bash

echo "Deploying Microbehaviour Backend..."

# Build Docker image
echo "Building Docker image..."
docker build -t microbehaviour-backend .

# Run container
echo "Starting backend container..."
docker run -d \
    --name microbehaviour-backend \
    -p 5000:5000 \
    -e FLASK_ENV=production \
    -e PORT=5000 \
    microbehaviour-backend

echo "Backend deployed successfully!"
echo "API available at: http://localhost:5000"
echo "Health check: http://localhost:5000/health"




