import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import joblib
import os

# -------------------------
# Dossiers
# -------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL_DIR = os.path.join(BASE_DIR, "..", "static", "models")

DIABETES_CSV = os.path.join(DATA_DIR, "diabetes.csv")
BREAST_CANCER_CSV = os.path.join(DATA_DIR, "brca.csv")

os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------
# Classe Diabetes
# -------------------------
class DiabetesPredictor:
    FEATURES = [
        "pregnancies", "glucose", "blood_pressure", "skin_thickness",
        "insulin", "bmi", "diabetes_pedigree", "age"
    ]

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    def _load_data(self):
        df = pd.read_csv(DIABETES_CSV)
        # Normalize column names from the dataset to expected feature keys
        col_map = {
            "pregnancies": "pregnancies",
            "glucose": "glucose",
            "bloodpressure": "blood_pressure",
            "blood_pressure": "blood_pressure",
            "skinthickness": "skin_thickness",
            "skin_thickness": "skin_thickness",
            "insulin": "insulin",
            "bmi": "bmi",
            "diabetespedigreefunction": "diabetes_pedigree",
            "diabetes_pedigree": "diabetes_pedigree",
            "age": "age",
            "outcome": "outcome",
        }
        rename = {}
        for col in df.columns:
            norm = col.strip().lower().replace(" ", "").replace(".", "").replace("_", "")
            if norm in col_map:
                rename[col] = col_map[norm]
        if rename:
            df = df.rename(columns=rename)
        df = df.drop_duplicates()
        df = df.fillna(df.median())
        return df

    def train(self):
        df = self._load_data()
        X, y = df[self.FEATURES], df["outcome"]
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_tr_s = self.scaler.fit_transform(X_tr)
        X_te_s = self.scaler.transform(X_te)
        self.model.fit(X_tr_s, y_tr)
        y_prob = self.model.predict_proba(X_te_s)[:, 1]
        print("Classification Report (Diabetes):\n", classification_report(y_te, self.model.predict(X_te_s)))
        return {
            "accuracy": round(self.model.score(X_te_s, y_te), 4),
            "auc": round(roc_auc_score(y_te, y_prob), 4),
        }

    def predict(self, feat):
        self._ensure_ready()
        vals = [feat.get(f, 0) for f in self.FEATURES]
        scaled = self.scaler.transform([vals])
        proba = self.model.predict_proba(scaled)[0][1]
        has_disease = proba >= 0.5
        if proba < 0.3:
            cat, grav, rec = "Risque faible", "surveillance", "Mode de vie sain. Controle annuel recommande."
        elif proba < 0.7:
            cat, grav, rec = "Risque modere", "differabe", "Consultation endocrinologie dans 3 mois. Surveillance glycemie."
        else:
            cat, grav, rec = "Risque eleve", "urgent", "Consultation urgente endocrinologie. HbA1c + glycemie a jeun requis."
        return {
            "score": int(proba * 1000),
            "probabilite": round(proba, 3),
            "has_disease": bool(has_disease),
            "categorie": cat,
            "gravite": grav,
            "recommandations": rec,
        }

    def save(self):
        joblib.dump(self.model, os.path.join(MODEL_DIR, "diabetes_model.pkl"))
        joblib.dump(self.scaler, os.path.join(MODEL_DIR, "diabetes_scaler.pkl"))

    def load(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "diabetes_model.pkl"))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, "diabetes_scaler.pkl"))

    def _is_trained(self):
        return hasattr(self.model, "estimators_") and hasattr(self.scaler, "mean_")

    def _ensure_ready(self):
        if self._is_trained():
            return
        try:
            self.load()
        except Exception:
            self.train()
            self.save()

# -------------------------
# Classe Breast Cancer
# -------------------------
class BreastCancerPredictor:
    FEATURES = [
        "radius_mean", "texture_mean", "perimeter_mean", "area_mean",
        "smoothness_mean", "compactness_mean", "concavity_mean",
        "concave_points_mean", "symmetry_mean", "fractal_dimension_mean"
    ]

    def __init__(self):
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()

    def _load_data(self):
        df = pd.read_csv(BREAST_CANCER_CSV, index_col=0)
        # Normalize column names from the BRCA dataset to expected feature keys
        rename = {}
        for col in df.columns:
            c = col.strip().lower()
            if c.startswith("x."):
                c = c[2:]
            if c == "y":
                c = "diagnosis"
            c = c.replace("concave_pts_", "concave_points_")
            c = c.replace("fractal_dim_", "fractal_dimension_")
            rename[col] = c
        if rename:
            df = df.rename(columns=rename)
        df = df.drop_duplicates()
        # Map target labels to numeric for model training
        if "diagnosis" in df.columns:
            df["diagnosis"] = df["diagnosis"].map({"B": 0, "M": 1}).fillna(df["diagnosis"])
        # Fill missing values only on numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        return df

    def train(self):
        df = self._load_data()
        X, y = df[self.FEATURES], df["diagnosis"]
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_tr_s = self.scaler.fit_transform(X_tr)
        X_te_s = self.scaler.transform(X_te)
        self.model.fit(X_tr_s, y_tr)
        y_prob = self.model.predict_proba(X_te_s)[:, 1]
        print("Classification Report (Breast Cancer):\n", classification_report(y_te, self.model.predict(X_te_s)))
        return {
            "accuracy": round(self.model.score(X_te_s, y_te), 4),
            "auc": round(roc_auc_score(y_te, y_prob), 4),
        }

    def predict(self, feat):
        self._ensure_ready()
        vals = [feat.get(f, 0) for f in self.FEATURES]
        scaled = self.scaler.transform([vals])
        proba = self.model.predict_proba(scaled)[0][1]
        has_disease = proba >= 0.5
        if proba < 0.2:
            cat, grav, rec = "Probablement benin", "surveillance", "Surveillance reguliere. Controle dans 6 mois."
        elif proba < 0.8:
            cat, grav, rec = "Suspicion - analyse requise", "differabe", "Biopsie recommandee. Consultation oncologie sous 15 jours."
        else:
            cat, grav, rec = "Forte suspicion maligne", "urgent", "Biopsie urgente. Consultation oncologie immediate. IRM complementaire."
        return {
            "score": int(proba * 1000),
            "probabilite": round(proba, 3),
            "has_disease": bool(has_disease),
            "categorie": cat,
            "gravite": grav,
            "recommandations": rec,
        }

    def save(self):
        joblib.dump(self.model, os.path.join(MODEL_DIR, "cancer_model.pkl"))
        joblib.dump(self.scaler, os.path.join(MODEL_DIR, "cancer_scaler.pkl"))

    def load(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "cancer_model.pkl"))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, "cancer_scaler.pkl"))

    def _is_trained(self):
        return hasattr(self.model, "coef_") and hasattr(self.scaler, "mean_")

    def _ensure_ready(self):
        if self._is_trained():
            return
        try:
            self.load()
        except Exception:
            self.train()
            self.save()

# -------------------------
# Entraînement
# -------------------------
def initialize_models():
    print("Training Diabetes model...")
    dm = DiabetesPredictor()
    dm_metrics = dm.train()
    dm.save()
    print(f"  Accuracy: {dm_metrics['accuracy']} | AUC: {dm_metrics['auc']}")

    print("Training Breast Cancer model...")
    cm = BreastCancerPredictor()
    cm_metrics = cm.train()
    cm.save()
    print(f"  Accuracy: {cm_metrics['accuracy']} | AUC: {cm_metrics['auc']}")

    return {"diabetes": dm_metrics, "cancer": cm_metrics}

if __name__ == "__main__":
    metrics = initialize_models()
    print("✅ Models trained and saved successfully!")
