import os
from dotenv import load_dotenv

# Charge le .env local si present (utile pour dev local)
load_dotenv()


def _get_env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and (val is None or str(val).strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


FLASK_ENV = _get_env("FLASK_ENV", default="development")
IS_PROD = FLASK_ENV.lower() == "production"


class Config:
    FLASK_ENV = FLASK_ENV
    IS_PROD = IS_PROD

    SECRET_KEY = _get_env(
        "SECRET_KEY",
        default="dev-secret" if not IS_PROD else None,
        required=IS_PROD,
    )

    SQLALCHEMY_DATABASE_URI = _get_env("DATABASE_URL", required=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MODELS_LOCAL_DIR = _get_env("MODELS_LOCAL_DIR", default=None)
