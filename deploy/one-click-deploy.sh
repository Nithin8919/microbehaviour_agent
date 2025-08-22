#!/bin/bash

echo "🚀 SUPER DUPER EASY DEPLOYMENT FOR MICROBEHAVIOUR 🚀"
echo "================================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please enter your OpenAI API key:"
    read -s openai_key
    echo "OPENAI_API_KEY=$openai_key" > .env
    echo "✅ Created .env file"
fi

echo "Choose your deployment platform:"
echo "1) 🟣 Heroku (Free tier available)"
echo "2) 🚂 Railway (Simple & fast)"
echo "3) 🎨 Render (Auto-deploy from GitHub)"
echo "4) ⚡ Vercel (Serverless)"
echo "5) 🐳 Docker (Local or any cloud)"
echo "6) 🔧 Manual setup instructions"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "🟣 Deploying to Heroku..."
        chmod +x deploy/deploy-to-heroku.sh
        ./deploy/deploy-to-heroku.sh
        ;;
    2)
        echo "🚂 Deploying to Railway..."
        chmod +x deploy/deploy-to-railway.sh
        ./deploy/deploy-to-railway.sh
        ;;
    3)
        echo "🎨 Setting up Render deployment..."
        chmod +x deploy/deploy-to-render.sh
        ./deploy/deploy-to-render.sh
        ;;
    4)
        echo "⚡ Deploying to Vercel..."
        echo "1. Install Vercel CLI: npm i -g vercel"
        echo "2. Run: vercel --local-config deploy/deploy-to-vercel.json"
        echo "3. Add OPENAI_API_KEY in Vercel dashboard"
        ;;
    5)
        echo "🐳 Setting up Docker deployment..."
        echo "Building Docker image..."
        docker build -t microbehaviour .
        echo "Starting with Docker Compose..."
        docker-compose up -d
        echo "✅ App running at http://localhost:5000"
        ;;
    6)
        echo "🔧 Manual deployment instructions:"
        echo "1. Set environment variable: OPENAI_API_KEY=your_key"
        echo "2. Install dependencies: pip install -r requirements.txt"
        echo "3. Run: python app/run.py"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "🎉 Deployment process started!"
echo "Visit your app once it's deployed to start analyzing user journeys!"
