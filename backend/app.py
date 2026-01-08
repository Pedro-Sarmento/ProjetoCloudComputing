from flask import Flask
from flask_cors import CORS
from .config import AppConfig
import os
import logging
import sys
from .register_routes import register_routes
from flask_sqlalchemy import SQLAlchemy
from startup import wait_for_db

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    cors = CORS()
    db.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {"origins": AppConfig.FRONTEND_URL},
        r"/snapshots/*": {"origins": AppConfig.FRONTEND_URL}
    }, supports_credentials=True)

    register_routes(app)

    with app.app_context():
        wait_for_db()     # uses POSTGRES_*; fine
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000, debug=True)