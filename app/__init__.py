from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="../static")
    from app.config import Config
    app.config.from_object(Config)

    @app.context_processor
    def inject_static_asset_url():
        def static_asset_url(path: str) -> str:
            from flask import url_for
            return url_for("static", filename=path)

        return {"static_asset_url": static_asset_url}

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
