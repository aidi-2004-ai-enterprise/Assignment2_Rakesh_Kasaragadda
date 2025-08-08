from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import xgboost as xgb
import os, joblib, logging
from dotenv import load_dotenv

# Optional import, only used if GCS is configured
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except Exception:
    GCS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("penguin-api")

load_dotenv()  # loads .env if present

# ---------- Pydantic contract ----------
class Island(str, Enum):
    Torgersen = "Torgersen"
    Biscoe = "Biscoe"
    Dream = "Dream"

class Sex(str, Enum):
    male = "male"
    female = "female"

class PenguinFeatures(BaseModel):
    # Add validation to force realistic ranges -> invalid values raise 422
    bill_length_mm: float = Field(gt=0, le=70, description="Bill length in mm (>0 and ≤70)")
    bill_depth_mm: float  = Field(gt=0, le=30, description="Bill depth in mm (>0 and ≤30)")
    flipper_length_mm: float = Field(gt=0, le=250, description="Flipper length in mm (>0 and ≤250)")
    body_mass_g: float = Field(gt=0, le=8000, description="Body mass in grams (>0 and ≤8000)")
    sex: Sex
    island: Island

# ---------- Paths & env ----------
APP_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(APP_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

LOCAL_MODEL_PATH   = os.path.join(DATA_DIR, "model.json")
LOCAL_ENCODER_PATH = os.path.join(DATA_DIR, "label_encoder.pkl")
LOCAL_COLUMNS_PATH = os.path.join(DATA_DIR, "columns.pkl")

GCS_BUCKET       = os.getenv("GCS_BUCKET_NAME")
GCS_MODEL_BLOB   = os.getenv("GCS_MODEL_BLOB", "model.json")
GCS_LABEL_BLOB   = os.getenv("GCS_LABEL_BLOB", "label_encoder.pkl")
GCS_COLUMNS_BLOB = os.getenv("GCS_COLUMNS_BLOB", "columns.pkl")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def download_from_gcs(bucket_name: str, blob_name: str, dst_path: str) -> None:
    if not GCS_AVAILABLE:
        raise RuntimeError("google-cloud-storage not available")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if not blob.exists(client):
        raise FileNotFoundError(f"gs://{bucket_name}/{blob_name} not found")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    blob.download_to_filename(dst_path)
    logger.info(f"Downloaded gs://{bucket_name}/{blob_name} -> {dst_path}")

def maybe_pull_from_gcs():
    if GCS_BUCKET and GOOGLE_APPLICATION_CREDENTIALS and GCS_AVAILABLE:
        logger.info("Attempting to pull model artifacts from GCS...")
        try:
            download_from_gcs(GCS_BUCKET, GCS_MODEL_BLOB,   LOCAL_MODEL_PATH)
            download_from_gcs(GCS_BUCKET, GCS_LABEL_BLOB,   LOCAL_ENCODER_PATH)
            download_from_gcs(GCS_BUCKET, GCS_COLUMNS_BLOB, LOCAL_COLUMNS_PATH)
            logger.info("Pulled all artifacts from GCS.")
        except Exception as e:
            logger.warning(f"GCS download failed: {e}. Falling back to local files.")
    else:
        logger.info("GCS not configured; using local files.")

# Pull artifacts if possible, else use local
maybe_pull_from_gcs()

# Load model + artifacts
model = xgb.XGBClassifier()
try:
    model.load_model(LOCAL_MODEL_PATH)
    label_encoder = joblib.load(LOCAL_ENCODER_PATH)
    columns       = joblib.load(LOCAL_COLUMNS_PATH)
    logger.info("Model and artifacts loaded.")
except Exception as e:
    logger.error(f"Failed to load artifacts: {e}")
    raise

app = FastAPI(title="Penguin Predictor")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(features: PenguinFeatures):
    try:
        df = pd.DataFrame([features.model_dump()])
        # match training normalization
        df["sex"] = df["sex"].str.lower()
        df["island"] = df["island"].str.capitalize()
        df = pd.get_dummies(df, columns=["sex", "island"])
        df = df.reindex(columns=columns, fill_value=0)

        pred = model.predict(df)[0]
        species = label_encoder.inverse_transform([int(pred)])[0]
        return {"prediction": species}
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")
