# Deployment Documentation

This document records how the app was containerized and deployed to Google Cloud Run, plus useful commands and observations.

---

## Docker Build & Run Commands

### Build the image
```bash
docker build -t penguin-api:local .
Run the container locally
docker run --rm -p 8080:8080 penguin-api:local
Local Test
Health: GET http://localhost:8080/health → {"status":"ok"}

Docs: http://localhost:8080/docs (Swagger UI)

Predict: /predict returns a species for valid input and 422 for invalid input (enforced by Pydantic Field ranges).

.dockerignore (key entries)

__pycache__
*.pyc
.env
.git
.gitignore
*.md
Resource Usage (sample)
From docker stats --no-stream during local run:

CPU Usage: ~0.2–0.5%

Memory Usage: ~120 MB

Image Inspection Summary
Command:

docker inspect penguin-api:local > image_inspect.json
From my inspect:

Image size: ~699 MB (JSON "Size" 732,394,752 bytes)

Layer count: 9 (count of "RootFS" → "Layers")

If you rebuild and get different numbers, update them here.

Artifact Registry
Repo: us-central1-docker.pkg.dev/rakeshassign2/penguin-repo

Image tag: penguin-api:latest

Commands used (when pushing a new build):

docker build -t us-central1-docker.pkg.dev/rakeshassign2/penguin-repo/penguin-api:latest .
docker push us-central1-docker.pkg.dev/rakeshassign2/penguin-repo/penguin-api:latest
Cloud Run Deployment
Service name: penguin-api

Region: us-central1

Image: us-central1-docker.pkg.dev/rakeshassign2/penguin-repo/penguin-api:latest

Port: 8080

Authentication: Allow unauthenticated

CPU/Memory: 1 vCPU / 512 MB (request-based)

Environment variables:

GCS_BUCKET_NAME = rakesh-penguin-model-2025

GCS_MODEL_BLOB = model.json

GCS_LABEL_BLOB = label_encoder.pkl

GCS_COLUMNS_BLOB = columns.pkl

Production URL
Base: https://penguin-api-810636854404.us-central1.run.app

Docs: https://penguin-api-810636854404.us-central1.run.app/docs

Smoke Test (curl)

curl -X GET "https://penguin-api-810636854404.us-central1.run.app/health"

curl -X POST "https://penguin-api-810636854404.us-central1.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "sex": "male",
        "island": "Torgersen"
      }'
Issues & Solutions
Read-only FS error while building: Fixed by rebuilding once docker’s unpack finished (Docker Desktop transient issue).

Port already allocated: Another process/container was using 8080. Stopped that container (or changed port) and re-ran.

GCS auth in container: Mounted service account key and set GOOGLE_APPLICATION_CREDENTIALS for local runs; on Cloud Run we use environment variables and the runtime pulls from GCS at startup.

Logs & Monitoring
Cloud Run → penguin-api → Logs tab (filter by severity).

Cold starts visible as slightly slower first request; autoscaling is min=0 by default (scales to zero when idle).

