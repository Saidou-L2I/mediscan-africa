import os
from pathlib import Path

import joblib
import pandas as pd


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        return None
    return str(value).strip()


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(_get_env("MODELS_LOCAL_DIR", str(BASE_DIR.parent / "static" / "models"))).resolve()
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_VERSION = "local"


def get_model_version() -> str:
    return MODEL_VERSION

DIABETES_MODEL_PATH = MODEL_DIR / "diabetes_model_final.pkl"
DIABETES_SCALER_PATH = MODEL_DIR / "diabetes_scaler_final.pkl"
DIABETES_POLY_PATH = MODEL_DIR / "diabetes_poly_final.pkl"
CANCER_MODEL_PATH = MODEL_DIR / "cancer_model_final.pkl"
CANCER_SCALER_PATH = MODEL_DIR / "cancer_scaler_final.pkl"

diabetes_model = joblib.load(DIABETES_MODEL_PATH)
diabetes_scaler = joblib.load(DIABETES_SCALER_PATH)
diabetes_poly = joblib.load(DIABETES_POLY_PATH)
cancer_model = joblib.load(CANCER_MODEL_PATH)
cancer_scaler = joblib.load(CANCER_SCALER_PATH)


def predict_diabetes(data: dict) -> dict:
    df = pd.DataFrame([data])
    features = [
        "pregnancies",
        "glucose",
        "blood_pressure",
        "skin_thickness",
        "insulin",
        "bmi",
        "diabetes_pedigree",
        "age",
    ]
    X = df[features]
    X_scaled = diabetes_scaler.transform(X)
    X_poly = diabetes_poly.transform(X_scaled)
    pred = int(diabetes_model.predict(X_poly)[0])
    proba = float(diabetes_model.predict_proba(X_poly)[0][1])

    if pred:
        cat, grav, rec = "Malade", "urgent", "Consultation rapide requise."
    else:
        cat, grav, rec = "Non malade", "surveillance", "Surveillance reguliere."

    return {
        "resultat": pred,
        "probabilite": round(proba, 3),
        "categorie": cat,
        "gravite": grav,
        "recommandations": rec,
    }


def predict_cancer(data: dict) -> dict:
    df = pd.DataFrame([data])
    features = [
        "radius_mean",
        "texture_mean",
        "perimeter_mean",
        "area_mean",
        "smoothness_mean",
        "compactness_mean",
        "concavity_mean",
        "concave_points_mean",
        "symmetry_mean",
        "fractal_dimension_mean",
    ]
    X = df[features]
    X_scaled = cancer_scaler.transform(X)
    pred = int(cancer_model.predict(X_scaled)[0])
    proba = float(cancer_model.predict_proba(X_scaled)[0][1])

    if pred:
        cat, grav, rec = "Malade", "urgent", "Consultation rapide requise."
    else:
        cat, grav, rec = "Non malade", "surveillance", "Surveillance reguliere."

    return {
        "resultat": pred,
        "probabilite": round(proba, 3),
        "categorie": cat,
        "gravite": grav,
        "recommandations": rec,
    }
