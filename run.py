import os
import sys
from app import create_app, db
from app.models import Patient, Consultation, ModeleHistorique

app = create_app()

try:
    with app.app_context():
        db.create_all()
except Exception as exc:
    print("Erreur de connexion a la base de donnees pendant l'initialisation.", file=sys.stderr)
    print(f"DATABASE_URL={app.config.get('SQLALCHEMY_DATABASE_URI')}", file=sys.stderr)
    print(f"Detail: {exc}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
