from app import db
from datetime import datetime
import json

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fictif = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    region_anonymisee = db.Column(db.String(50))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    consultations = db.relationship("Consultation", backref="patient", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nom_fictif": self.nom_fictif,
            "age": self.age,
            "sexe": self.sexe,
            "region_anonymisee": self.region_anonymisee,
            "date_creation": self.date_creation.isoformat()
        }


class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    date_consultation = db.Column(db.DateTime, default=datetime.utcnow)
    scenario_type = db.Column(db.String(50), nullable=False)
    symptomes_json = db.Column(db.Text, nullable=False)
    score_risque = db.Column(db.Float, nullable=False)
    diagnostic_principal = db.Column(db.String(200), nullable=False)
    recommandations = db.Column(db.Text)
    gravite = db.Column(db.String(20))
    medecin_fictif = db.Column(db.String(100))

    def set_symptomes(self, d):
        self.symptomes_json = json.dumps(d)

    def get_symptomes(self):
        return json.loads(self.symptomes_json) if self.symptomes_json else {}

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "date_consultation": self.date_consultation.isoformat(),
            "scenario_type": self.scenario_type,
            "score_risque": self.score_risque,
            "diagnostic_principal": self.diagnostic_principal,
            "recommandations": self.recommandations,
            "gravite": self.gravite,
        }


class ModeleHistorique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    scenario_type = db.Column(db.String(50), nullable=False)
    date_deploy = db.Column(db.DateTime, default=datetime.utcnow)
    metriques_json = db.Column(db.Text)
    actif = db.Column(db.Boolean, default=True)

    def set_metriques(self, d):
        self.metriques_json = json.dumps(d)

    def get_metriques(self):
        return json.loads(self.metriques_json) if self.metriques_json else {}