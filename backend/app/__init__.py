import os

from dotenv import load_dotenv
from flask import Flask;
from flask_migrate import Migrate;
from flask_sqlalchemy import SQLAlchemy;

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")

    if not database_url and not test_config:
        raise RuntimeError("DATABASE URL is not configured.")

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Tests can override the real database connection.
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    from app.routes import api

    app.register_blueprint(api)

    #from app.routes import api imports the API Blueprint from another Python module.
    # from app.routes import api
    # app.register_blueprint(api)   #app.register_blueprint(api) connects those routes to the application

    #This pattern is called the Application Factory Pattern. It makes it easier to create different application instances for development and automated tests

    return app