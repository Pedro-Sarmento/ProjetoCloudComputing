import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"   
    SESSION_COOKIE_SECURE = False     

    FRONTEND_ORIGINS = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]
