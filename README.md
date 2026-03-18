# MediScan Africa - Plateforme IA de Detection de Maladies

## Description
Plateforme d'aide au diagnostic medical utilisant l'IA pour les professionnels de sante.

## Scenarios ML
- Diabete Type 2 (Random Forest)
- Cancer du Sein (Logistic Regression)

## Installation locale

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python scripts/init_db.py
    python run.py

Puis ouvrir http://localhost:5000

## Deploiement AWS
Voir AWS_DEPLOYMENT_GUIDE.md