from flask import Flask
from config import Config
from extensions import cors
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from services.csrf_service import issue_csrf_token
from flask import jsonify
from flask import redirect

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.FLASK_SECRET_KEY

    if not app.secret_key:
        raise RuntimeError("FLASK_SECRET_KEY is not set in environment/.env")

    app.config.update(
        SESSION_COOKIE_HTTPONLY=Config.SESSION_COOKIE_HTTPONLY,
        SESSION_COOKIE_SAMESITE=Config.SESSION_COOKIE_SAMESITE,
        SESSION_COOKIE_SECURE=Config.SESSION_COOKIE_SECURE,
    )

    cors.init_app(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": Config.FRONTEND_ORIGINS}},
    )

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return redirect("https://pedro-sarmento.github.io/ProjetoCloudComputing/frontEnd/login.html")
    
    @app.get("/api/csrf")
    def csrf():
        return jsonify({"csrf_token": issue_csrf_token()})

    return app


