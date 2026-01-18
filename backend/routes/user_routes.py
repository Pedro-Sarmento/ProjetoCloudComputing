from flask import Blueprint, jsonify, session
from firebase_startup import db

user_bp = Blueprint("user", __name__)

@user_bp.get("/me")
def me():
    username = session.get("username")
    if not username:
        return jsonify({"logged_in": False}), 200

    profile = db.child("users").child(username).get().val()
    if profile:
        profile.pop("password_hash", None) 

    return jsonify({"logged_in": True, "profile": profile}), 200

