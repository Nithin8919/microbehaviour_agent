#!/bin/bash

echo "Deploying Microbehaviour Backend and Frontend..."

# Deploy backend
echo "=== Deploying Backend ==="
./deploy-backend.sh

# Wait a moment for backend to start
sleep 5

# Deploy frontend
echo "=== Deploying Frontend ==="
./deploy-frontend.sh

echo "=== Deployment Complete ==="
echo "Backend API: http://localhost:5000"
echo "Frontend: http://localhost:8000"
echo "Health Check: http://localhost:5000/health"




