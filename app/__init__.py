from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # ---- FIXED DB PATH ----
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(basedir, "dev.db")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{db_path}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    # register routes
    from .routes import main
    app.register_blueprint(main)

    from .routes_calendar import calendar_bp
    app.register_blueprint(calendar_bp)

    # create tables on first run
    with app.app_context():
        db.create_all()

    return app
