import os
from dotenv import load_dotenv

# Charge le .env local si present
load_dotenv()
load_dotenv("/home/ubuntu/.env", override=False)

def _get_env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and (val is None or str(val).strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

FLASK_ENV = os.environ.get("FLASK_ENV", "development")
IS_PROD = FLASK_ENV.lower() == "production"

class Config:
    FLASK_ENV = FLASK_ENV
    SECRET_KEY = _get_env("SECRET_KEY", default=None if IS_PROD else "dev-secret", required=IS_PROD)
    SQLALCHEMY_DATABASE_URI = _get_env(
        "DATABASE_URL",
        default=None if IS_PROD else "sqlite:///mediscan.db",
        required=IS_PROD,
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_REGION = _get_env("AWS_REGION", default="us-east-1")
    S3_BUCKET = _get_env("S3_BUCKET", default=None if IS_PROD else "mediscan-africa-models-2024")
