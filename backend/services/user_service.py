from typing import Optional, Dict, Any

def get_profile(db, uid: str) -> Optional[Dict[str, Any]]:
    return db.child("users").child(uid).get().val()

def username_lookup(db, username_key: str):
    return db.child("usernames").child(username_key).get().val()

def set_profile(db, uid: str, profile: dict) -> None:
    db.child("users").child(uid).set(profile)

def set_username_index(db, username_key: str, uid: str) -> None:
    db.child("usernames").child(username_key).set({"uid": uid})
