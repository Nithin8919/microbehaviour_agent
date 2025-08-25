#!/bin/bash

echo "🚂 Deploying to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
railway login

# Create new project or link existing
echo "Create a new Railway project? (y/n)"
read create_new

if [ "$create_new" = "y" ]; then
    railway project new
else
    railway link
fi

# Set environment variables
echo "Please enter your OpenAI API key:"
read -s openai_key
railway variables set OPENAI_API_KEY="$openai_key"

# Deploy
railway up

echo "✅ Deployment complete! Your app should be live shortly."
echo "Visit your Railway dashboard to see the deployment URL."
