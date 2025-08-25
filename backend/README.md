# Microbehaviour Backend

This directory contains the backend API and core microbehaviour analysis functionality.

## Structure

- `microbehaviour/` - Core analysis modules
- `app/` - Application-specific code
- `deploy/` - Deployment configurations
- `tests/` - Test files
- `main.py` - Main Flask application entry point

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the backend:
   ```bash
   python main.py
   ```

3. Or use Docker:
   ```bash
   docker build -t microbehaviour-backend .
   docker run -p 5000:5000 microbehaviour-backend
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze` - Analyze user journey
- `POST /api/scrape` - Scrape website data

## Environment Variables

- `PORT` - Server port (default: 5000)
- `FLASK_ENV` - Flask environment (default: production)

## Deployment

Use the deployment scripts in the `deploy/` directory or run from root:
```bash
./deploy-backend.sh
```


