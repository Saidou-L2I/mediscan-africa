from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app import db
from app.model_inference import get_model_version, predict_cancer, predict_diabetes
from app.models import Consultation, Patient

bp = Blueprint("main", __name__)


def _predict_by_scenario(scenario: str, features: dict) -> tuple[dict, str]:
    if scenario == "diabete":
        result = predict_diabetes(features)
        return result, f"Diabete Type 2 - {result['categorie']}"
    if scenario == "cancer_sein":
        result = predict_cancer(features)
        return result, f"Cancer du Sein - {result['categorie']}"
    raise ValueError("Scenario non supporte")


def _save_consultation(scenario: str, features: dict, patient_info: dict, result: dict, diagnostic_principal: str):
    patient = Patient(
        nom_fictif=patient_info.get("nom", "Anonyme"),
        age=int(patient_info.get("age", 30)),
        sexe=patient_info.get("sexe", "M"),
        region_anonymisee=patient_info.get("region", "Non specifiee"),
    )
    db.session.add(patient)
    db.session.flush()

    consultation = Consultation(
        patient_id=patient.id,
        scenario_type=scenario,
        score_risque=float(result.get("probabilite", 0.0)),
        diagnostic_principal=diagnostic_principal,
        recommandations=result["recommandations"],
        gravite=result["gravite"],
        medecin_fictif="Dr. IA MediScan",
    )
    consultation.set_symptomes(features)
    db.session.add(consultation)
    db.session.commit()
    return patient, consultation


@bp.route("/")
def index():
    stats = {
        "total_consultations": Consultation.query.count(),
        "total_patients": Patient.query.count(),
        "consultations_diabete": Consultation.query.filter_by(scenario_type="diabete").count(),
        "consultations_cancer": Consultation.query.filter_by(scenario_type="cancer_sein").count(),
    }
    recentes = Consultation.query.order_by(Consultation.date_consultation.desc()).limit(5).all()
    return render_template("index.html", stats=stats, recentes=recentes)


@bp.route("/diagnostic/<scenario>")
def diagnostic_form(scenario):
    if scenario not in ("diabete", "cancer_sein"):
        flash("Scenario non valide", "danger")
        return redirect(url_for("main.index"))
    return render_template("diagnostic.html", scenario=scenario)


@bp.route("/diagnostic", methods=["POST"])
@bp.route("/api/diagnostic", methods=["POST"])
def api_diagnostic():
    try:
        data = request.get_json(silent=True) or {}
        scenario = data.get("scenario")
        features = data.get("features", {})
        patient_info = data.get("patient", {})

        if scenario not in ("diabete", "cancer_sein"):
            return jsonify({"error": "Scenario non supporte"}), 400
        if not isinstance(features, dict):
            return jsonify({"error": "features doit etre un objet JSON"}), 400

        model_version = get_model_version()

        result, diagnostic_principal = _predict_by_scenario(scenario, features)
        patient, consultation = _save_consultation(
            scenario, features, patient_info, result, diagnostic_principal
        )
        payload = {
            "consultation_id": consultation.id,
            "patient_id": patient.id,
            "resultat": result["resultat"],
            "probabilite": result.get("probabilite"),
            "categorie": result["categorie"],
            "diagnostic": diagnostic_principal,
            "recommandations": result["recommandations"],
            "gravite": result["gravite"],
            "timestamp": consultation.date_consultation.isoformat(),
        }
        return jsonify({"cached": False, "model_version": model_version, **payload}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500


@bp.route("/patient/<int:patient_id>/historique", methods=["GET"])
@bp.route("/api/patient/<int:patient_id>/historique", methods=["GET"])
def patient_historique(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    consultations = (
        Consultation.query.filter_by(patient_id=patient_id)
        .order_by(Consultation.date_consultation.desc())
        .all()
    )
    return jsonify(
        {
            "patient": patient.to_dict(),
            "historique": [c.to_dict() for c in consultations],
            "total": len(consultations),
        }
    )


@bp.route("/stats/aggregees", methods=["GET"])
@bp.route("/api/stats", methods=["GET"])
def stats_aggregees():
    total = Consultation.query.count()
    if total == 0:
        return jsonify(
            {
                "nombre_diagnostics": 0,
                "taux_par_pathologie": {},
                "score_risque_moyen": 0,
            }
        )

    grouped = (
        db.session.query(Consultation.scenario_type, db.func.count(Consultation.id))
        .group_by(Consultation.scenario_type)
        .all()
    )
    avg_risk = db.session.query(db.func.avg(Consultation.score_risque)).scalar() or 0.0
    rates = {scenario: round((count / total) * 100, 2) for scenario, count in grouped}
    return jsonify(
        {
            "nombre_diagnostics": total,
            "taux_par_pathologie": rates,
            "score_risque_moyen": round(float(avg_risk), 4),
        }
    )


@bp.route("/results/<int:consultation_id>")
def results(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    patient = Patient.query.get(consultation.patient_id)
    return render_template("results.html", consultation=consultation, patient=patient)


@bp.route("/historique")
def historique():
    page = request.args.get("page", 1, type=int)
    consultations = Consultation.query.order_by(Consultation.date_consultation.desc()).paginate(
        page=page, per_page=10
    )
    return render_template("historique.html", consultations=consultations)


@bp.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500
