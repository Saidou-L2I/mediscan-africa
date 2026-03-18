import sys
import os
sys.path.insert(0, "/opt/mediscan-africa")

from app import create_app, db

application = create_app()

with application.app_context():
    db.create_all()

if __name__ == "__main__":
    application.run()