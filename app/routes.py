from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Patient, Consultation, ModeleHistorique
from app.ml_models import DiabetesPredictor, BreastCancerPredictor
from datetime import datetime
import os

bp = Blueprint("main", __name__)

diabetes_predictor = DiabetesPredictor()
cancer_predictor = BreastCancerPredictor()

try:
    diabetes_predictor.load()
    cancer_predictor.load()
except Exception:
    pass  # Models will be trained on first use


@bp.route("/")
def index():
    stats = {
        "total_consultations": Consultation.query.count(),
        "total_patients": Patient.query.count(),
        "consultations_diabete": Consultation.query.filter_by(scenario_type="diabete").count(),
        "consultations_cancer": Consultation.query.filter_by(scenario_type="cancer_sein").count(),
    }
    recentes = (
        Consultation.query.order_by(Consultation.date_consultation.desc()).limit(5).all()
    )
    return render_template("index.html", stats=stats, recentes=recentes)


@bp.route("/diagnostic/<scenario>")
def diagnostic_form(scenario):
    if scenario not in ("diabete", "cancer_sein"):
        flash("Scenario non valide", "danger")
        return redirect(url_for("main.index"))
    return render_template("diagnostic.html", scenario=scenario)


@bp.route("/api/diagnostic", methods=["POST"])
def api_diagnostic():
    try:
        data = request.get_json()
        scenario = data.get("scenario")
        features = data.get("features", {})
        patient_info = data.get("patient", {})

        patient = Patient(
            nom_fictif=patient_info.get("nom", "Anonyme"),
            age=int(patient_info.get("age", 30)),
            sexe=patient_info.get("sexe", "M"),
            region_anonymisee=patient_info.get("region", "Non specifiee"),
        )
        db.session.add(patient)
        db.session.flush()

        if scenario == "diabete":
            result = diabetes_predictor.predict(features)
            diagnostic_principal = "Diabete Type 2 - " + result["categorie"]
        elif scenario == "cancer_sein":
            result = cancer_predictor.predict(features)
            diagnostic_principal = "Cancer du Sein - " + result["categorie"]
        else:
            return jsonify({"error": "Scenario non supporte"}), 400

        consultation = Consultation(
            patient_id=patient.id,
            scenario_type=scenario,
            score_risque=result["probabilite"],
            diagnostic_principal=diagnostic_principal,
            recommandations=result["recommandations"],
            gravite=result["gravite"],
            medecin_fictif="Dr. IA MediScan",
        )
        consultation.set_symptomes(features)
        db.session.add(consultation)
        db.session.commit()

        return jsonify({
            "consultation_id": consultation.id,
            "patient_id": patient.id,
            "score": result["score"],
            "probabilite": result["probabilite"],
            "categorie": result["categorie"],
            "diagnostic": diagnostic_principal,
            "has_disease": result["has_disease"],
            "recommandations": result["recommandations"],
            "gravite": result["gravite"],
            "timestamp": consultation.date_consultation.isoformat(),
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/results/<int:consultation_id>")
def results(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    patient = Patient.query.get(consultation.patient_id)
    return render_template("results.html", consultation=consultation, patient=patient)


@bp.route("/historique")
def historique():
    page = request.args.get("page", 1, type=int)
    consultations = (
        Consultation.query.order_by(Consultation.date_consultation.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("historique.html", consultations=consultations)


@bp.route("/api/stats")
def api_stats():
    total = Consultation.query.count()
    if total == 0:
        return jsonify({"total": 0, "patients": 0, "score_moyen": 0,
                        "gravite": {}, "scenarios": {}})

    gravites = db.session.query(Consultation.gravite, db.func.count()).group_by(Consultation.gravite).all()
    scenarios = db.session.query(Consultation.scenario_type, db.func.count()).group_by(Consultation.scenario_type).all()
    score_moy = db.session.query(db.func.avg(Consultation.score_risque)).scalar() or 0

    return jsonify({
        "total": total,
        "patients": Patient.query.count(),
        "score_moyen": round(score_moy * 1000, 1),
        "gravite": {g[0]: g[1] for g in gravites},
        "scenarios": {s[0]: s[1] for s in scenarios},
    })


@bp.route("/train")
def train():
    try:
        from app.ml_models import initialize_models
        metrics = initialize_models()
        diabetes_predictor.load()
        cancer_predictor.load()
        flash("Modeles entraines avec succes !", "success")
    except Exception as e:
        flash("Erreur : " + str(e), "danger")
    return redirect(url_for("main.index"))


@bp.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
