import os
from pathlib import Path
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
BASE_DIR = Path(__file__).resolve().parent.parent


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
    SQLALCHEMY_ENGINE_OPTIONS = {}

    if SQLALCHEMY_DATABASE_URI.startswith("mysql+pymysql://"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "connect_timeout": 5,
                "read_timeout": 5,
                "write_timeout": 5,
            }
        }

    MODELS_LOCAL_DIR = _get_env("MODELS_LOCAL_DIR", default=None)


if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite:///"):
    sqlite_path = Config.SQLALCHEMY_DATABASE_URI.removeprefix("sqlite:///")
    resolved_sqlite_path = (BASE_DIR / sqlite_path).resolve()
    resolved_sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    Config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{resolved_sqlite_path.as_posix()}"
