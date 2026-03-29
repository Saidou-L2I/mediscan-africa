"""import os
import sys
from pathlib import Path

import joblib
import pandas as pd

from app.feature_engineers import DiabetesFeatureEngineer, FeatureEngineering


sys.modules["__main__"].DiabetesFeatureEngineer = DiabetesFeatureEngineer
sys.modules["__main__"].FeatureEngineering = FeatureEngineering


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(
    os.environ.get("MODELS_LOCAL_DIR", str(BASE_DIR.parent / "static" / "models"))
).resolve()
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_VERSION = "local"


def get_model_version() -> str:
    return MODEL_VERSION


DIABETES_MODEL_PATH = MODEL_DIR / "best_diabetes_pipeline.pkl"
CANCER_MODEL_PATH = MODEL_DIR / "best_breast_cancer_pipeline.pkl"

diabetes_model = joblib.load(DIABETES_MODEL_PATH)
cancer_model = joblib.load(CANCER_MODEL_PATH)


DIABETES_INPUT_ALIASES = {
    "Pregnancies": ["Pregnancies", "pregnancies"],
    "Glucose": ["Glucose", "glucose"],
    "BloodPressure": ["BloodPressure", "blood_pressure"],
    "SkinThickness": ["SkinThickness", "skin_thickness"],
    "Insulin": ["Insulin", "insulin"],
    "BMI": ["BMI", "bmi"],
    "DiabetesPedigreeFunction": [
        "DiabetesPedigreeFunction",
        "diabetes_pedigree",
        "diabetes_pedigree_function",
    ],
    "Age": ["Age", "age", "age_feature"],
}

CANCER_INPUT_ALIASES = {
    "x.radius_mean": ["x.radius_mean", "radius_mean"],
    "x.texture_mean": ["x.texture_mean", "texture_mean"],
    "x.perimeter_mean": ["x.perimeter_mean", "perimeter_mean"],
    "x.area_mean": ["x.area_mean", "area_mean"],
    "x.smoothness_mean": ["x.smoothness_mean", "smoothness_mean"],
    "x.compactness_mean": ["x.compactness_mean", "compactness_mean"],
    "x.concavity_mean": ["x.concavity_mean", "concavity_mean"],
    "x.concave_pts_mean": ["x.concave_pts_mean", "concave_points_mean", "x.concave_points_mean"],
    "x.symmetry_mean": ["x.symmetry_mean", "symmetry_mean"],
    "x.fractal_dim_mean": ["x.fractal_dim_mean", "fractal_dimension_mean", "fractal_dim_mean"],
    "x.radius_se": ["x.radius_se", "radius_se"],
    "x.texture_se": ["x.texture_se", "texture_se"],
    "x.perimeter_se": ["x.perimeter_se", "perimeter_se"],
    "x.area_se": ["x.area_se", "area_se"],
    "x.smoothness_se": ["x.smoothness_se", "smoothness_se"],
    "x.compactness_se": ["x.compactness_se", "compactness_se"],
    "x.concavity_se": ["x.concavity_se", "concavity_se"],
    "x.concave_pts_se": ["x.concave_pts_se", "concave_points_se", "x.concave_points_se"],
    "x.symmetry_se": ["x.symmetry_se", "symmetry_se"],
    "x.fractal_dim_se": ["x.fractal_dim_se", "fractal_dimension_se", "fractal_dim_se"],
    "x.radius_worst": ["x.radius_worst", "radius_worst"],
    "x.texture_worst": ["x.texture_worst", "texture_worst"],
    "x.perimeter_worst": ["x.perimeter_worst", "perimeter_worst"],
    "x.area_worst": ["x.area_worst", "area_worst"],
    "x.smoothness_worst": ["x.smoothness_worst", "smoothness_worst"],
    "x.compactness_worst": ["x.compactness_worst", "compactness_worst"],
    "x.concavity_worst": ["x.concavity_worst", "concavity_worst"],
    "x.concave_pts_worst": ["x.concave_pts_worst", "concave_points_worst", "x.concave_points_worst"],
    "x.symmetry_worst": ["x.symmetry_worst", "symmetry_worst"],
    "x.fractal_dim_worst": ["x.fractal_dim_worst", "fractal_dimension_worst", "fractal_dim_worst"],
}


def _coerce_numeric(value, default=0.0) -> float:
    if value is None or value == "":
        return float(default)
    return float(value)


def _normalize_input(data: dict, aliases: dict[str, list[str]]) -> pd.DataFrame:
    normalized = {}
    for canonical_name, keys in aliases.items():
        value = None
        for key in keys:
            if key in data:
                value = data[key]
                break
        normalized[canonical_name] = _coerce_numeric(value, default=0.0)
    return pd.DataFrame([normalized])


def predict_diabetes(data: dict) -> dict:
    try:
        X = _normalize_input(data, DIABETES_INPUT_ALIASES)
        pred = int(diabetes_model.predict(X)[0])
        proba = float(diabetes_model.predict_proba(X)[0][1])

        if pred:
            cat, grav, rec = "Malade", "urgent", "Consultation rapide requise."
        else:
            cat, grav, rec = "Non malade", "surveillance", "Surveillance reguliere."

        return {
            "modele": "diabete",
            "version": get_model_version(),
            "resultat": pred,
            "probabilite": round(proba, 3),
            "categorie": cat,
            "gravite": grav,
            "recommandations": rec,
        }
    except Exception as exc:
        return {"erreur": str(exc)}


def predict_cancer(data: dict) -> dict:
    try:
        X = _normalize_input(data, CANCER_INPUT_ALIASES)
        pred = int(cancer_model.predict(X)[0])
        proba = float(cancer_model.predict_proba(X)[0][1])

        if pred:
            cat, grav, rec = "Malade", "urgent", "Consultation rapide requise."
        else:
            cat, grav, rec = "Non malade", "surveillance", "Surveillance reguliere."

        return {
            "modele": "cancer",
            "version": get_model_version(),
            "resultat": pred,
            "probabilite": round(proba, 3),
            "categorie": cat,
            "gravite": grav,
            "recommandations": rec,
        }
    except Exception as exc:
        return {"erreur": str(exc)}
"""
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(
    os.environ.get("MODELS_LOCAL_DIR", str(BASE_DIR.parent / "static" / "models"))
).resolve()

MODEL_VERSION = "v1-final"

def get_model_version():
    return MODEL_VERSION

# =========================
# LOAD MODELS
# =========================
# Diabetes
diabetes_model = joblib.load(MODEL_DIR / "diabetes_model_final.pkl")
diabetes_scaler = joblib.load(MODEL_DIR / "diabetes_scaler_final.pkl")
diabetes_poly = joblib.load(MODEL_DIR / "diabetes_poly_final.pkl")

# Cancer
cancer_model = joblib.load(MODEL_DIR / "cancer_model_final.pkl")
cancer_scaler = joblib.load(MODEL_DIR / "cancer_scaler_final.pkl")

# =========================
# INPUT ALIASES
# =========================
DIABETES_INPUT_ALIASES = {
    "pregnancies": ["Pregnancies", "pregnancies"],
    "glucose": ["Glucose", "glucose"],
    "blood_pressure": ["BloodPressure", "blood_pressure"],
    "skin_thickness": ["SkinThickness", "skin_thickness"],
    "insulin": ["Insulin", "insulin"],
    "bmi": ["BMI", "bmi"],
    "diabetes_pedigree": [
        "DiabetesPedigreeFunction",
        "diabetes_pedigree",
        "diabetes_pedigree_function",
    ],
    "age": ["Age", "age"],
}

CANCER_INPUT_ALIASES = {
    "radius_mean": ["x.radius_mean", "radius_mean"],
    "texture_mean": ["x.texture_mean", "texture_mean"],
    "perimeter_mean": ["x.perimeter_mean", "perimeter_mean"],
    "area_mean": ["x.area_mean", "area_mean"],
    "smoothness_mean": ["x.smoothness_mean", "smoothness_mean"],
    "compactness_mean": ["x.compactness_mean", "compactness_mean"],
    "concavity_mean": ["x.concavity_mean", "concavity_mean"],
    "concave_points_mean": ["x.concave_pts_mean", "concave_points_mean"],
    "symmetry_mean": ["x.symmetry_mean", "symmetry_mean"],
    "fractal_dimension_mean": ["x.fractal_dim_mean", "fractal_dimension_mean"],
    "radius_se": ["x.radius_se", "radius_se"],
    "texture_se": ["x.texture_se", "texture_se"],
    "perimeter_se": ["x.perimeter_se", "perimeter_se"],
    "area_se": ["x.area_se", "area_se"],
    "smoothness_se": ["x.smoothness_se", "smoothness_se"],
    "compactness_se": ["x.compactness_se", "compactness_se"],
    "concavity_se": ["x.concavity_se", "concavity_se"],
    "concave_points_se": ["x.concave_pts_se", "concave_points_se"],
    "symmetry_se": ["x.symmetry_se", "symmetry_se"],
    "fractal_dimension_se": ["x.fractal_dim_se", "fractal_dimension_se"],
    "radius_worst": ["x.radius_worst", "radius_worst"],
    "texture_worst": ["x.texture_worst", "texture_worst"],
    "perimeter_worst": ["x.perimeter_worst", "perimeter_worst"],
    "area_worst": ["x.area_worst", "area_worst"],
    "smoothness_worst": ["x.smoothness_worst", "smoothness_worst"],
    "compactness_worst": ["x.compactness_worst", "compactness_worst"],
    "concavity_worst": ["x.concavity_worst", "concavity_worst"],
    "concave_points_worst": ["x.concave_pts_worst", "concave_points_worst"],
    "symmetry_worst": ["x.symmetry_worst", "symmetry_worst"],
    "fractal_dimension_worst": ["x.fractal_dim_worst", "fractal_dimension_worst"],
}

# =========================
# UTILS
# =========================
def _coerce_numeric(value, default=None):
    if value is None or value == "":
        return float(default)
    return float(value)

def _normalize_input(data: dict, aliases: dict):
    normalized = {}
    for canonical_name, keys in aliases.items():
        value = None
        for key in keys:
            if key in data:
                value = data[key]
                break
        normalized[canonical_name] = _coerce_numeric(value)
    return pd.DataFrame([normalized])

# =========================
# FEATURE ENGINEERING DIABETES
# =========================
def _diabetes_feature_engineering(df):
    df["bmi_age"] = df["bmi"] * df["age"]
    df["glucose_ratio"] = df["glucose"] / (df["age"] + 1)
    df["insulin_log"] = np.log(df["insulin"] + 1)
    df["skin_bmi"] = df["skin_thickness"] * df["bmi"]
    df["preg_glucose"] = df["pregnancies"] * df["glucose"]
    df["glucose_insulin"] = df["glucose"] / (df["insulin"] + 1)
    df["bmi_squared"] = df["bmi"] ** 2
    df["age_squared"] = df["age"] ** 2
    df["glucose_squared"] = df["glucose"] ** 2
    return df

# =========================
# PREDICT DIABETES
# =========================
def predict_diabetes(data: dict):
    try:
        X = _normalize_input(data, DIABETES_INPUT_ALIASES)

        # Feature engineering
        X = _diabetes_feature_engineering(X)

        # Transformations
        X_scaled = diabetes_scaler.transform(X)
        X_poly = diabetes_poly.transform(X_scaled)

        pred = int(diabetes_model.predict(X_poly)[0])
        proba = float(diabetes_model.predict_proba(X_poly)[0][1])

        return {
            "modele": "diabete",
            "version": get_model_version(),
            "resultat": pred,
            "probabilite": round(proba, 3),
            "categorie": "Malade" if pred else "Non malade",
            "gravite": "urgent" if pred else "surveillance",
            "recommandations": "Consultation rapide requise." if pred else "Surveillance reguliere."
        }

    except Exception as e:
        return {"erreur": str(e)}

# =========================
# PREDICT CANCER
# =========================
def predict_cancer(data: dict):
    try:
        X = _normalize_input(data, CANCER_INPUT_ALIASES)

        # Scaling
        X_scaled = cancer_scaler.transform(X)

        pred = int(cancer_model.predict(X_scaled)[0])
        proba = float(cancer_model.predict_proba(X_scaled)[0][1])

        return {
            "modele": "cancer",
            "version": get_model_version(),
            "resultat": pred,
            "probabilite": round(proba, 3),
            "categorie": "Malade" if pred else "Non malade",
            "gravite": "urgent" if pred else "surveillance",
            "recommandations": "Consultation rapide requise." if pred else "Surveillance reguliere."
        }

    except Exception as e:
        return {"erreur": str(e)}