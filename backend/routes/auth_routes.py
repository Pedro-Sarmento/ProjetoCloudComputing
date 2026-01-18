from flask import Blueprint, request, jsonify, session
from services.csrf_service import require_csrf, issue_csrf_token
from services.auth_service import make_email, firebase_register, firebase_login
from services.user_service import (
    username_lookup,
    set_profile,
    set_username_index,
    get_profile,
)

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    from firebase_startup import auth, db

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
        existing = username_lookup(db, username_key)
    except Exception:
        existing = None
    if existing:
        return jsonify({"error": "Username already taken"}), 400

    email = make_email(student_number)

    try:
        uid = firebase_register(auth, email, password)
    except Exception:
        return jsonify({"error": "Could not create user (maybe already exists)."}), 400

    profile = {
        "username": username,
        "studentNumber": student_number,
        "age": age,
        "course": course,
    }

    try:
        set_profile(db, uid, profile)
    except Exception:
        return jsonify({"error": "User created but failed saving profile."}), 500

    try:
        set_username_index(db, username_key, uid)
    except Exception:
        return jsonify({"error": "User created but username index failed."}), 500

    return jsonify({"ok": True, "uid": uid})


@auth_bp.post("/login")
def login():
    from firebase_startup import auth, db

    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        lookup = username_lookup(db, username)
    except Exception:
        return jsonify({"error": "Login failed"}), 400

    if not lookup or "uid" not in lookup:
        return jsonify({"error": "Invalid credentials"}), 401

    uid = lookup["uid"]

    try:
        profile = get_profile(db, uid)
    except Exception:
        return jsonify({"error": "Login failed"}), 400

    if not profile or "studentNumber" not in profile:
        return jsonify({"error": "Login failed"}), 400

    email = make_email(profile["studentNumber"])

    try:
        user = firebase_login(auth, email, password)
    except Exception:
        return jsonify({"error": "Invalid credentials"}), 401

    session["uid"] = uid
    session["idToken"] = user.get("idToken")
    issue_csrf_token() 

    return jsonify({"ok": True})


@auth_bp.post("/logout")
def logout():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403
    session.clear()
    return jsonify({"ok": True})
