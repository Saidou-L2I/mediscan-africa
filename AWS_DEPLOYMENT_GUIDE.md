# Guide de Deploiement AWS Free Tier - MediScan Africa

## Services utilises (100% gratuits)
- EC2 t2.micro : 750h/mois gratuit
- RDS db.t3.micro PostgreSQL : 750h/mois gratuit
- S3 : 5GB gratuit
- Elastic IP : gratuit si attachee a une instance active

---

## ETAPE 1 - Prérequis

1. Créer un compte AWS sur https://aws.amazon.com
2. Activer la region us-east-1 (moins chere)
3. Installer AWS CLI : pip install awscli
4. Configurer : aws configure

---

## ETAPE 2 - Créer la base de données RDS (Free Tier)

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
11. Security group : créer "mediscan-rds-sg"
12. Créer la base

Copier le endpoint RDS (ex: mediscan.xxxxx.us-east-1.rds.amazonaws.com)

---

## ETAPE 3 - Créer le bucket S3 (Free Tier)

    aws s3 mb s3://mediscan-africa-models-2024 --region us-east-1

---

## ETAPE 4 - Lancer l'instance EC2 (Free Tier)

Via la console AWS :
1. EC2 > Launch instance
2. Name : MediScan-Africa
3. AMI : Amazon Linux 2023 (gratuite)
4. Instance type : t2.micro (FREE TIER ELIGIBLE)
5. Key pair : créer "mediscan-key" et télécharger le .pem
6. Security group : créer "mediscan-sg"
   - Inbound : HTTP 80 from 0.0.0.0/0
   - Inbound : HTTPS 443 from 0.0.0.0/0
   - Inbound : SSH 22 from MY IP
7. Storage : 8 GB gp2 (gratuit)
8. User data : coller le contenu de aws/user-data.sh
   (Modifier DATABASE_URL avec votre endpoint RDS !)
9. Launch instance

---

## ETAPE 5 - Se connecter et verifier

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

## ETAPE 6 - Acceder a l'application

Ouvrir : http://VOTRE-IP-PUBLIQUE

1. Cliquer sur "Entrainer IA" pour initialiser les modeles
2. Tester le diagnostic Diabete
3. Tester le diagnostic Cancer du Sein

---

## ETAPE 7 - Modifier user-data.sh AVANT le déploiement

Remplacer ces valeurs dans aws/user-data.sh :
- VOTRE_RDS_ENDPOINT : endpoint copié à l'étape 2
- VOTRE_USERNAME : votre nom d'utilisateur GitHub
- votre-secret-key-production : une chaine aléatoire longue

---

## ETAPE 8 - Mise a jour de l'application

    ssh -i mediscan-key.pem ec2-user@VOTRE-IP
    cd /opt/mediscan-africa
    sudo git pull origin main
    sudo systemctl restart mediscan

---

## ETAPE 9 - Arreter pour economiser (important Free Tier)

    # Arreter l instance (stockage conserve, pas d heures consommees)
    aws ec2 stop-instances --instance-ids VOTRE-INSTANCE-ID

    # Redemarrer
    aws ec2 start-instances --instance-ids VOTRE-INSTANCE-ID

---

## ETAPE 10 - Alertes de facturation (OBLIGATOIRE)

1. AWS Console > Billing > Budgets
2. Create budget > Cost budget
3. Amount : $5
4. Email alert : votre@email.com

---

## Checklist finale

[ ] Compte AWS verifie
[ ] RDS db.t3.micro cree (FREE TIER)
[ ] S3 bucket cree
[ ] EC2 t2.micro lance (FREE TIER)
[ ] Security groups configures
[ ] user-data.sh modifie avec les bons endpoints
[ ] Application accessible via HTTP
[ ] Modeles ML entraines (cliquer Entrainer IA)
[ ] Alerte facturation configuree a 5$

---

Bonne chance pour votre deploiement !