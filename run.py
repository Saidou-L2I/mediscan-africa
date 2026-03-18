import os
from app import create_app, db
from app.models import Patient, Consultation, ModeleHistorique

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)