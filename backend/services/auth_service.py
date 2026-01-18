def make_email(student_number: str) -> str:
    return f"{student_number}@project.cloudcomputing"

def firebase_register(auth, email: str, password: str) -> str:
    user = auth.create_user_with_email_and_password(email, password)
    return user["localId"]

def firebase_login(auth, email: str, password: str) -> dict:
    return auth.sign_in_with_email_and_password(email, password)
