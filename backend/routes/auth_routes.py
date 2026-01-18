from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from services.csrf_service import require_csrf, issue_csrf_token
from firebase_startup import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403

    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    student_number = (data.get("studentNumber") or "").strip()
    course = data.get("course")

    age_raw = data.get("age")
    try:
        age = int(age_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid age"}), 400

    if not username or not password or not student_number or not course:
        return jsonify({"error": "Missing required fields"}), 400
    if age <= 0:
        return jsonify({"error": "Invalid age"}), 400

    try:
        if db.child("users").child(username).get().val():
            return jsonify({"error": "Username already exists"}), 400
    except Exception:
        return jsonify({"error": "Database error"}), 500

    password_hash = generate_password_hash(password)

    try:
        db.child("users").child(username).set({
            "username": username,
            "password_hash": password_hash,
            "studentNumber": student_number,
            "age": age,
            "course": course
        })
    except Exception as e:
        return jsonify({"error": "Something went wrong saving user"}), 500

    return jsonify({"ok": True}), 201


@auth_bp.post("/login")
def login():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        user = db.child("users").child(username).get().val()
    except Exception:
        return jsonify({"error": "Database error"}), 500

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["username"] = username

    issue_csrf_token()

    return jsonify({"ok": True}), 200


@auth_bp.post("/logout")
def logout():
    if not require_csrf():
        return jsonify({"error": "CSRF check failed"}), 403

    session.clear()

    issue_csrf_token()

    return jsonify({"ok": True}), 200
