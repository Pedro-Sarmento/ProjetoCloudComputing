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

@app.get("/api/me")
def me():
    uid = session.get("uid")
    if not uid:
        return jsonify({"logged_in": False}), 200
    
    try:
        profile = db.child("users").child(uid).get().val()
    
    except Exception:
        profile = None
    
    return jsonify({"logged_in": True, "uid": uid, "profile": profile}), 200

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

    
    username_key = username.lower()

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age"}), 400
    if age <= 0:
        return jsonify({"error": "Invalid age"}), 400

    
    try:
        existing = db.child("usernames").child(username_key).get().val()
    except Exception:
        existing = None
    if existing:
        return jsonify({"error": "Username already taken"}), 400


    email = f"{student_number}@project.cloudcomputing"

   
    try:
        user = auth.create_user_with_email_and_password(email, password)
        uid = user["localId"]
    except Exception:
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

    try:
        db.child("usernames").child(username_key).set({"uid": uid})
    except Exception:
        return jsonify({"error": "User created but username index failed."}), 500

    return jsonify({"ok": True, "uid": uid})


@app.post("/api/login")
def login():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

  
    try:
        lookup = db.child("usernames").child(username).get().val()
    except Exception:
        return jsonify({"error": "Login failed"}), 400

    if not lookup or "uid" not in lookup:
        return jsonify({"error": "Invalid credentials"}), 401

    uid = lookup["uid"]

 
    try:
        profile = db.child("users").child(uid).get().val()
    except Exception:
        return jsonify({"error": "Login failed"}), 400

    if not profile or "studentNumber" not in profile:
        return jsonify({"error": "Login failed"}), 400

    email = f'{profile["studentNumber"]}@project.cloudcomputing'


    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except Exception:
        return jsonify({"error": "Invalid credentials"}), 401

    session["uid"] = uid
    session["idToken"] = user.get("idToken")

    
    issue_csrf_token()

    return jsonify({"ok": True})


@app.post("/api/logout")
def logout():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403
    session.clear()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )
    app.run(host="127.0.0.1", port=5000, debug=True)