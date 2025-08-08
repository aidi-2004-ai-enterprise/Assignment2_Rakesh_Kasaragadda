# Deployment Documentation

## Docker Build & Run Commands
```bash
# Build the image
docker build -t penguin-api:local .

# Run the container locally
docker run --rm -p 8080:8080 penguin-api:local

.dockerignore
nginx
Copy
Edit
__pycache__
*.pyc
.env
.git
.gitignore
*.md
Local Testing
Health Check: /health endpoint responds correctly with HTTP 200.

Prediction: /predict endpoint returns correct species predictions matching non-containerized app.

Tested via FastAPI Swagger UI (/docs) and cURL.

Resource Usage
From docker stats:

yaml
Copy
Edit
CPU Usage: ~0.22%
Memory Usage: ~122 MB
Image Inspection Summary
Command used: docker inspect penguin-api:local

Image size: ~699 MB

Layer count: 9

Base image: python:3.10-slim

Exposed port: 8080

Entrypoint/CMD: uvicorn app.main:app --host 0.0.0.0 --port 8080

Environment variables: PORT=8080, PYTHONDONTWRITEBYTECODE=1, PYTHONUNBUFFERED=1

Observations
Using .dockerignore reduced build context size and improved build time.

Slim Python base image significantly reduced image size compared to full python:3.10.

No sensitive data or secrets baked into the image.

The application runs identically inside and outside the container.

Issues & Solutions
Issue: Docker Desktop Linux engine not running caused initial cannot find //./pipe/dockerDesktopLinuxEngine error.

Solution: Restarted Docker Desktop and ensured Linux containers were enabled.
