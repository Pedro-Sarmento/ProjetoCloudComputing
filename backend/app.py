import os
import secrets
from flask import Flask, request, jsonify, session 
from flask_cors import CORS
from firebase_startup import auth, db

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}},
)


def issue_csrf_token() -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token

def require_csrf():
    sent = request.headers.get("X-CSRF-Token")
    expected = session.get("csrf_token")
    if not expected or not sent or sent != expected:
        return False
    return True

@app.get("/api/csrf")
def csrf():
    return jsonify({"csrf_token": issue_csrf_token()})

@app.post("/api/register")
def register():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403 

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    student_number = (data.get("studentNumber") or "").strip()
    password = data.get("password") or ""
    age = data.get("age")
    course = data.get("course")

    if not username or not student_number or not password or not course:
        return jsonify({"error": "Missing required fields"}), 400
    if not isinstance(age, int) or age <= 0:
        return jsonify({"error": "Invalid age"}), 400


    email = f"{student_number}@project.cloudcomputing"

    try:
        user = auth.create_user_with_email_and_password(email, password)
        uid = user["localId"]
    except Exception as e:
        return jsonify({"error": "Could not create user (maybe already exists)."}), 400

    profile = {
        "username": username,
        "studentNumber": student_number,
        "age": age,
        "course": course,
    }

    try:
        db.child("users").child(uid).set(profile)
    except Exception:
        return jsonify({"error": "User created but failed saving profile."}), 500

    return jsonify({"ok": True, "uid": uid})

if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )
    app.run(host="127.0.0.1", port=5000, debug=True)