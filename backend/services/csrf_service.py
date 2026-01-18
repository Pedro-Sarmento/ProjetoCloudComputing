import secrets
from flask import request, session

def issue_csrf_token() -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token

def require_csrf() -> bool:
    sent = request.headers.get("X-CSRF-Token")
    expected = session.get("csrf_token")
    return bool(expected and sent and sent == expected)
