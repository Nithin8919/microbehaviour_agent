# Microbehaviour Analysis Tool

A tool for analyzing user behavior and micro-interactions on websites.

## Project Structure

This project is organized into two main components:

- **`backend/`** - Python Flask API and core analysis functionality
- **`frontend/`** - Web interface and static assets

## Quick Start

### Option 1: Deploy Everything at Once
```bash
./deploy-all.sh
```

### Option 2: Deploy Separately

#### Backend
```bash
./deploy-backend.sh
```

#### Frontend
```bash
./deploy-frontend.sh
```

## Manual Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
./build.sh
cd build
python -m http.server 8000
```

## Access Points

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:8000
- **Health Check**: http://localhost:5000/health

## Docker Deployment

```bash
# Backend
cd backend
docker-compose up -d

# Frontend
cd frontend
./deploy/deploy-frontend.sh
```

## Development

- Backend code is in the `backend/` directory
- Frontend code is in the `frontend/` directory
- Each component has its own README with detailed instructions

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze` - Analyze user journey
- `POST /api/scrape` - Scrape website data

## Requirements

- Python 3.8+
- Docker (optional)
- Modern web browser





