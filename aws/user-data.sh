#!/bin/bash
set -e
exec > /var/log/mediscan-init.log 2>&1

echo "=== MediScan Africa - Installation ==="
yum update -y
yum install -y python3 python3-pip git nginx awscli

pip3 install virtualenv

cd /opt
#==le repo github===
git clone https://github.com/Saidou-L2I/mediscan-africa.git
cd mediscan-africa

python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

SSM_PREFIX="/mediscan"
IMDS_TOKEN="$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)"
if [ -n "$IMDS_TOKEN" ]; then
  AWS_REGION="$(curl -s -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" http://169.254.169.254/latest/meta-data/placement/region)"
else
  AWS_REGION="us-east-1"
fi
SECRET_KEY="$(aws ssm get-parameter --region "$AWS_REGION" --name "${SSM_PREFIX}/SECRET_KEY" --with-decryption --query "Parameter.Value" --output text)"
DATABASE_URL="$(aws ssm get-parameter --region "$AWS_REGION" --name "${SSM_PREFIX}/DATABASE_URL" --with-decryption --query "Parameter.Value" --output text)"
S3_BUCKET="$(aws ssm get-parameter --region "$AWS_REGION" --name "${SSM_PREFIX}/S3_BUCKET" --query "Parameter.Value" --output text)"

cat > /etc/environment <<EOF
SECRET_KEY="${SECRET_KEY}"
DATABASE_URL="${DATABASE_URL}"
FLASK_ENV="production"
S3_BUCKET="${S3_BUCKET}"
AWS_REGION="${AWS_REGION}"
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
