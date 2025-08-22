#!/bin/bash

echo "🟣 Deploying to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "Please install Heroku CLI first:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login to Heroku
heroku login

# Create app name
echo "Enter your app name (or press Enter for auto-generated):"
read app_name

if [ -z "$app_name" ]; then
    heroku create
else
    heroku create "$app_name"
fi

# Set environment variables
echo "Please enter your OpenAI API key:"
read -s openai_key
heroku config:set OPENAI_API_KEY="$openai_key"

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

echo "✅ Deployment complete!"
heroku open
