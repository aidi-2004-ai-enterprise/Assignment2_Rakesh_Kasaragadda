# Assignment2_Rakesh_Kasaragadda
# 🐧 Penguin Classifier API – Assignment 2  
**Course:** AIDI-2004 – Applied Machine Learning and Advanced AI Systems  
**Author:** Rakesh Kasaragadda  

---

## 📌 Project Overview
This project implements a **machine learning inference API** using **FastAPI** to classify penguin species based on physical measurements. The API is containerized with Docker, deployed to Google Cloud Run, and tested under production-like load using Locust.

The app:
- Loads a trained **XGBoost** model and encoders from **Google Cloud Storage (GCS)** at startup.
- Validates inputs with **Pydantic** for strict type and range enforcement.
- Exposes a `/predict` endpoint for inference and `/health` for status checks.
- Has automated **unit tests** for valid/invalid predictions, data validation, and model load.

---

## 🚀 Deployment Links
**Production API URL:**  
[https://penguin-api-810636854404.us-central1.run.app](https://penguin-api-810636854404.us-central1.run.app)  

**Swagger API Docs:**  
[https://penguin-api-810636854404.us-central1.run.app/docs](https://penguin-api-810636854404.us-central1.run.app/docs)

---

## 📂 Repository Structure
Assignment2_Rakesh_Kasaragadda/
├── app/
│ ├── main.py # FastAPI app, model loading, endpoints
│ ├── init.py
│ ├── utils.py # Helper functions for GCS model pull
│ └── requirements.txt
├── tests/
│ ├── test_api.py # API endpoint tests
│ └── test_validation.py # Input validation tests
├── Dockerfile
├── .dockerignore
├── DEPLOYMENT.md # Build & deploy steps (local + GCP)
├── LOAD_TEST_REPORT.md # Locust results, bottlenecks, recommendations
├── README.md
└── requirements.txt



---

## 🛠️ Local Development

### 1️⃣ Clone the repo
```bash
git clone https://github.com/aidi-2004-ai-enterprise/Assignment2_Rakesh_Kasaragadda.git
cd Assignment2_Rakesh_Kasaragadda
2️⃣ Create and activate venv

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
3️⃣ Install dependencies

pip install -r requirements.txt
4️⃣ Set environment variables

export GCP_PROJECT=my-gcp-project
export GCP_BUCKET=rakesh-penguin-model-2025
export MODEL_BLOB=model.json
export ENCODER_BLOB=label_encoder.pkl
export COLUMNS_BLOB=columns.pkl
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
5️⃣ Run locally

uvicorn app.main:app --reload --port 8080
Visit: http://localhost:8080/docs

🐳 Docker (Local)
Build image

docker build -t penguin-api .
Run container

docker run -p 8080:8080 --env-file .env penguin-api
☁️ Deployment (Cloud Run)
Steps are in detail in DEPLOYMENT.md, but the short version:

gcloud builds submit --tag us-central1-docker.pkg.dev/<project-id>/<repo>/penguin-api
gcloud run deploy penguin-api \
  --image us-central1-docker.pkg.dev/<project-id>/<repo>/penguin-api \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account=penguin-api-sa@<project-id>.iam.gserviceaccount.com
🧪 Running Tests

pytest --cov=app tests/
Sample output:

---------- coverage: platform win32, python 3.10 ----------
Name           Stmts   Miss  Cover
----------------------------------
app/main.py       52     12    77%
tests/test_*.py   30      0   100%
📊 Load Testing (Locust)
We tested only on the deployed Cloud Run URL as per instructor’s updated instructions.

Scenarios tested:

Baseline: 5 users, 1 spawn rate, 2 min

Normal: 10 users, 1 spawn rate, 5 min

Stress: 50 users, 5 spawn rate, 2 min

Spike: 100 users, 100 spawn rate, 1 min

Summary: See LOAD_TEST_REPORT.md for:

Response time percentiles

Failure rates

Throughput

Bottleneck analysis

Scaling recommendations

❓ Q&A
Q1: What edge cases might break the model?

Out-of-distribution inputs (impossible measurements, unseen categories).

Extreme values near boundaries (mitigated by Pydantic range checks).

Missing/wrong data types (blocked by FastAPI validation).

Q2: What happens if the model file is corrupted?

Startup will fail and API returns 500.

Mitigation: add checksum verification, keep last-known-good model, use GCS versioning.

Q3: Realistic load for this classifier?

Academic/demo usage: <20 RPS.

Cloud Run sustained ~7–70 RPS depending on scenario.

Q4: How to optimize slow response times?

Increase min instances to reduce cold starts.

Adjust CPU/memory in Cloud Run.

Ensure model loads once at startup (already implemented).

Q5: Important production metrics for ML APIs?

Latency (P50/P95/P99), throughput, error rate, cold starts, CPU/mem usage.

Q6: Why does Docker layer caching matter?

Speeds up rebuilds by reusing unchanged layers.

Our Dockerfile copies requirements.txt first, installs deps, then copies code.

Q7: Risks of running containers as root?

Higher privilege escalation risk.

Prefer non-root user in production for security.

Q8: How does auto-scaling affect load test results?

Cold starts during spikes cause temporary latency/failures until scale-out completes.

Q9: What if traffic increases 10×?

More cold starts, possible timeouts.

Increase max instances, concurrency, min instances.

Q10: How to monitor in production?

Use Cloud Monitoring for latency, errors, and scaling metrics.

Set alerts on high P95 latency and 5xx errors.

Q11: Blue-green deployment approach?

Deploy new revision in parallel, route small % traffic, roll back instantly if needed.

Q12: What if deployment fails?

Roll back to last working revision.

Verify image tag, env vars, and logs.

Q13: What if container uses too much memory?

Cloud Run OOM-kills instance.

Increase memory limit, optimize memory usage, reduce data copies.

