from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_predict_valid():
    payload = {
        "bill_length_mm": 45.2,
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        "body_mass_g": 4500,
        "sex": "male",
        "island": "Biscoe"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "prediction" in body
    assert body["prediction"] in {"Adelie", "Gentoo", "Chinstrap"}

def test_missing_field():
    payload = {
        "bill_length_mm": 45.2,
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        # "body_mass_g" missing on purpose
        "sex": "male",
        "island": "Biscoe"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 422

def test_invalid_type():
    payload = {
        "bill_length_mm": "oops",   # invalid type
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        "body_mass_g": 4500,
        "sex": "male",
        "island": "Biscoe"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 422

def test_out_of_range_negative():
    payload = {
        "bill_length_mm": 45.2,
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        "body_mass_g": -1,  # invalid (gt=0)
        "sex": "male",
        "island": "Biscoe"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 422

def test_invalid_enum():
    payload = {
        "bill_length_mm": 45.2,
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        "body_mass_g": 4500,
        "sex": "unknown",   # invalid enum
        "island": "Biscoe"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 422

def test_empty_body():
    r = client.post("/predict", json={})
    assert r.status_code == 422
