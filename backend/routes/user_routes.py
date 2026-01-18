from flask import Blueprint, jsonify, session
from services.user_service import get_profile

user_bp = Blueprint("user", __name__)

@user_bp.get("/me")
def me():
    from firebase_startup import db

    uid = session.get("uid")
    if not uid:
        return jsonify({"logged_in": False}), 200

    try:
        profile = get_profile(db, uid)
    except Exception:
        profile = None

    return jsonify({"logged_in": True, "uid": uid, "profile": profile}), 200
