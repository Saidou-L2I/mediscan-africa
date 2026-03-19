#!/bin/bash
set -e
exec > /var/log/mediscan-init.log 2>&1

echo "=== MediScan Africa - Installation ==="
yum update -y
yum install -y python3 python3-pip git nginx

pip3 install virtualenv

cd /opt
#==le repo github===
git clone https://github.com/Saidou-L2I/mediscan-africa.git
cd mediscan-africa

python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

cat > /etc/environment <<EOF
SECRET_KEY="votre-secret-key-production"
DATABASE_URL="postgresql://mediscanadmin:mediscan#2026@VOTRE_RDS_ENDPOINT:5432/mediscan"
FLASK_ENV="production"
S3_BUCKET="mediscan-africa-models"
EOF

source /etc/environment
python scripts/init_db.py
python -c "from app.ml_models import initialize_models; initialize_models()"

cp aws/nginx.conf /etc/nginx/conf.d/mediscan.conf
rm -f /etc/nginx/conf.d/default.conf

cat > /etc/systemd/system/mediscan.service <<UNIT
[Unit]
Description=MediScan Africa
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/opt/mediscan-africa
EnvironmentFile=/etc/environment
ExecStart=/opt/mediscan-africa/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    aws.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable mediscan
systemctl start mediscan
systemctl enable nginx
systemctl start nginx

echo "=== Installation terminee ==="