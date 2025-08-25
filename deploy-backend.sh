#!/bin/bash

echo "Deploying Microbehaviour Backend from root directory..."

# Change to backend directory
cd backend

# Run backend deployment
./deploy/deploy-backend.sh

echo "Backend deployment completed!"
