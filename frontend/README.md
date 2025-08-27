# Microbehaviour Frontend

This directory contains the frontend web interface for the microbehaviour analysis tool.

## Structure

- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and other static assets
- `screenshots/` - Example screenshots
- `build/` - Build output directory (created by build script)

## Quick Start

1. Build the frontend:
   ```bash
   ./build.sh
   ```

2. Serve the frontend:
   ```bash
   cd build
   python -m http.server 8000
   ```

3. Or use the deployment script:
   ```bash
   ./deploy/deploy-frontend.sh
   ```

## Build Process

The `build.sh` script:
- Creates a `build/` directory
- Copies all static assets
- Copies HTML templates
- Creates a default index.html if none exists

## Deployment

Use the deployment scripts in the `deploy/` directory or run from root:
```bash
./deploy-frontend.sh
```

## Connecting to Backend

The frontend is designed to communicate with the backend API running on port 5000. Make sure the backend is running before using the frontend.




