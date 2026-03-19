# Guide de Deploiement AWS Free Tier - MediScan Africa

## Services utilises (Free Tier)
- EC2 t2.micro : 750h/mois gratuit
- RDS db.t3.micro PostgreSQL : 750h/mois gratuit
- S3 : 5GB gratuit
- Lambda : 1M requetes / 400k GB-s (gratuit)
- VPC : gratuit (utiliser le VPC par defaut)
- CloudWatch : logs/metrics de base gratuits
- Elastic IP : gratuit si attachee a une instance active

## Architecture cible (exigee par le prof)
- VPC avec 1 sous-reseau public + 1 sous-reseau prive
- EC2 en public (serveur web + API)
- RDS en prive (pas d acces public)
- S3 pour stocker les modeles/artefacts ML
- Lambda pour taches courtes (ex: verification S3, nettoyage, ou entrainement planifie)
- CloudWatch pour logs EC2/Lambda et alertes

---

## ETAPE 1 - Prerequis

1. Creer un compte AWS sur https://aws.amazon.com
2. Activer la region us-east-1 (moins chere)
3. Installer AWS CLI : pip install awscli
4. Configurer : aws configure

---

## ETAPE 2 - VPC et reseaux (obligatoire)

Si vous n'avez pas de VPC personnalisee, utilisez le VPC par defaut (simple).
Sinon creez un VPC avec 2 sous-reseaux :
- Public subnet (EC2)
- Private subnet (RDS)

Associer les tables de routage :
- Public subnet -> Internet Gateway
- Private subnet -> pas d acces Internet direct

---

## ETAPE 3 - Creer la base de donnees RDS (Free Tier)

Via la console AWS :
1. Aller dans RDS > Create database
2. Standard Create
3. Engine : PostgreSQL
4. Template : FREE TIER (important !)
5. DB instance : db.t3.micro
6. DB name : mediscan
7. Master user : mediscanadmin
8. Password : MediScan2024!
9. Storage : 20 GB gp2
10. Public access : No
11. Security group : creer "mediscan-rds-sg"
    - Inbound PostgreSQL 5432 depuis le security group EC2/Lambda uniquement
12. Creer la base

Copier le endpoint RDS (ex: mediscan.xxxxx.us-east-1.rds.amazonaws.com)

---

## ETAPE 4 - Creer le bucket S3 (Free Tier)

    aws s3 mb s3://mediscan-africa-models-2024 --region us-east-1

---

## ETAPE 5 - Lancer l'instance EC2 (Free Tier)

Via la console AWS :
1. EC2 > Launch instance
2. Name : MediScan-Africa
3. AMI : Amazon Linux 2023 (gratuite)
4. Instance type : t2.micro (FREE TIER ELIGIBLE)
5. Key pair : creer "mediscan-key" et telecharger le .pem
6. Security group : creer "mediscan-sg"
   - Inbound : HTTP 80 from 0.0.0.0/0
   - Inbound : HTTPS 443 from 0.0.0.0/0
   - Inbound : SSH 22 from MY IP
7. Storage : 8 GB gp2 (gratuit)
8. User data : coller le contenu de aws/user-data.sh
   (Modifier DATABASE_URL avec votre endpoint RDS !)
9. Launch instance

---

## ETAPE 6 - Se connecter et verifier

    chmod 400 mediscan-key.pem
    ssh -i mediscan-key.pem ec2-user@VOTRE-IP-PUBLIQUE

    # Verifier les logs
    sudo tail -f /var/log/mediscan-init.log

    # Verifier les services
    sudo systemctl status mediscan
    sudo systemctl status nginx

    # Tester
    curl http://localhost/health

---

## ETAPE 7 - Acceder a l'application

Ouvrir : http://VOTRE-IP-PUBLIQUE

1. Cliquer sur "Entrainer IA" pour initialiser les modeles
2. Tester le diagnostic Diabete
3. Tester le diagnostic Cancer du Sein

---

## ETAPE 8 - Modifier user-data.sh AVANT le deploiement

Remplacer ces valeurs dans aws/user-data.sh :
- VOTRE_RDS_ENDPOINT : endpoint copie a l'etape 3
- VOTRE_USERNAME : votre nom d'utilisateur GitHub
- votre-secret-key-production : une chaine aleatoire longue

---

## ETAPE 9 - Mise a jour de l'application

    ssh -i mediscan-key.pem ec2-user@VOTRE-IP
    cd /opt/mediscan-africa
    sudo git pull origin main
    sudo systemctl restart mediscan

---

## ETAPE 10 - Arreter pour economiser (important Free Tier)

    # Arreter l instance (stockage conserve, pas d heures consommees)
    aws ec2 stop-instances --instance-ids VOTRE-INSTANCE-ID

    # Redemarrer
    aws ec2 start-instances --instance-ids VOTRE-INSTANCE-ID

---

## ETAPE 11 - Lambda (exigence prof)

Creer une fonction Lambda simple pour valider la presence des modeles dans S3.
Exemple (console Lambda) :
1. Runtime : Python 3.11
2. Role : creer un role avec permissions S3 read-only + CloudWatch Logs
3. Code (inline) :

```python
import os
import boto3

s3 = boto3.client("s3")
BUCKET = os.environ.get("BUCKET_NAME")

def lambda_handler(event, context):
    if not BUCKET:
        return {"ok": False, "error": "BUCKET_NAME manquant"}
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix="models/")
    count = resp.get("KeyCount", 0)
    return {"ok": True, "models": count}
```

4. Ajouter la variable d'environnement `BUCKET_NAME`
5. Tester la fonction
6. (Optionnel) Programmer via EventBridge (1 fois/jour)

---

## ETAPE 12 - CloudWatch (exigence prof)

- EC2 : verifier que les logs d'initialisation sont dans `/var/log/mediscan-init.log`
- Lambda : logs automatiques dans CloudWatch Logs
- Creer une alerte basique (CPU > 80%) pour l'instance EC2

---

## ETAPE 13 - Alertes de facturation (OBLIGATOIRE)

1. AWS Console > Billing > Budgets
2. Create budget > Cost budget
3. Amount : $5
4. Email alert : votre@email.com

---

## Checklist finale

[ ] Compte AWS verifie
[ ] VPC et sous-reseaux ok
[ ] RDS db.t3.micro cree (FREE TIER)
[ ] S3 bucket cree
[ ] EC2 t2.micro lance (FREE TIER)
[ ] Lambda creee et testee
[ ] CloudWatch logs/alertes ok
[ ] Security groups configures
[ ] user-data.sh modifie avec les bons endpoints
[ ] Application accessible via HTTP
[ ] Modeles ML entraines (cliquer Entrainer IA)
[ ] Alerte facturation configuree a 5$

---

Bonne chance pour votre deploiement !
