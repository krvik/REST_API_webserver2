from flask import Flask
from api.src.extensions import db
from api.src.routes.students_v1 import students_v1
from api.src.routes.students_v2 import students_v2
from api.src.routes.students_legacy import students_legacy

import os


def create_app():
    app = Flask(__name__)

    # Fallback default database (required for tests + GitHub Actions)
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

    # If running in production and DATABASE_URL exists, override it
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        app.config["SQLALCHEMY_DATABASE_URI"] = env_db

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(students_v1, url_prefix="/api/v1/students")
    app.register_blueprint(students_v2, url_prefix="/api/v2/students")
    app.register_blueprint(students_legacy, url_prefix="/students")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
