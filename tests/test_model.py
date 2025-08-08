import pandas as pd
from app.main import model, label_encoder, columns

def test_model_direct_prediction_runs():
    # Build a row that matches training columns
    row = {c: 0 for c in columns}
    row.update({
        "bill_length_mm": 45.2,
        "bill_depth_mm": 17.8,
        "flipper_length_mm": 210,
        "body_mass_g": 4500,
    })
    if "sex_male" in row: row["sex_male"] = 1
    if "island_Biscoe" in row: row["island_Biscoe"] = 1

    df = pd.DataFrame([row], columns=columns)
    pred = model.predict(df)[0]
    species = label_encoder.inverse_transform([int(pred)])[0]
    assert species in {"Adelie", "Gentoo", "Chinstrap"}
