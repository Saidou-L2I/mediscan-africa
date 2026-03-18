import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-mediscan")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mediscan.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_BUCKET = os.environ.get("S3_BUCKET", "mediscan-africa-models")