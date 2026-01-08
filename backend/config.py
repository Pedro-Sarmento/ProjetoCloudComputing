import os
def get_database_uri() -> str:
    uri =os.getenv("DB_URL")
    if uri:
        return uri
    
    raise RuntimeError("No database URI found in env (SQLALCHEMY_DATABASE_URI / DATABASE_URL / POSTGRES_*).")

class AppConfig:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", os.getenv("SECRET_KEY", "change-me"))
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_URL = os.getenv("FRONTEND_ORIGIN", os.getenv("FRONTEND_URL", "*"))

    SESSION_COOKIE_SECURE   = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax" 