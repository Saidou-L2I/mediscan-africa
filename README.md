# MediScan Africa - Plateforme IA de Detection de Maladies

## Description
Plateforme d'aide au diagnostic medical utilisant l'IA pour les professionnels de sante.

## Modele ML
- Un seul modele `model.pkl` (entraine sur Colab) utilise en inference.

## Installation locale (MySQL requis)

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    # Configurer MySQL via .env (DATABASE_URL) - obligatoire
    python scripts/init_db.py
    python run.py

Puis ouvrir http://localhost:5000

## Modele unique (Colab)
Place les fichiers de modele dans `static/models/`. L'app ne fait pas d'entrainement local.

## Deploiement direct

1. Installer MySQL et creer une base (ex: `mediscan_db`).
2. Copier `.env.example` vers `.env` et mettre a jour `DATABASE_URL` (obligatoire).
3. Lancer les migrations/tables puis demarrer l'app :

    python scripts/init_db.py
    gunicorn -w 2 -b 0.0.0.0:5000 run:app

## API
- `POST /diagnostic` (compatible aussi `POST /api/diagnostic`)
- `GET /patient/<id>/historique`
- `GET /stats/aggregees` (compatible aussi `GET /api/stats`)
