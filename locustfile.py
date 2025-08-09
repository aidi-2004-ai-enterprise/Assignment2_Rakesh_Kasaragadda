from locust import HttpUser, task, between
import random

# Realistic ranges (match your Pydantic Field limits)
def valid_payload():
    return {
        "bill_length_mm": round(random.uniform(32.0, 60.0), 1),
        "bill_depth_mm": round(random.uniform(13.0, 22.0), 1),
        "flipper_length_mm": random.randint(170, 230),
        "body_mass_g": random.randint(3000, 6000),
        "sex": random.choice(["male", "female"]),
        "island": random.choice(["Torgersen", "Biscoe", "Dream"]),
    }

def invalid_payload():
    # guaranteed invalid: negative value triggers 422
    bad = valid_payload()
    bad["body_mass_g"] = -100
    return bad

class PenguinUser(HttpUser):
    # small wait between tasks to simulate real users
    wait_time = between(0.5, 2.0)

    @task(8)
    def predict_ok(self):
        self.client.post("/predict", json=valid_payload(), timeout=10)

    @task(2)
    def predict_bad(self):
        # Expected to return 422 sometimes (counts as failure in Locust UI, but note it's intentional)
        self.client.post("/predict", json=invalid_payload(), timeout=10)
