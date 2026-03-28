import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

_initialized = False


def _initialize():
    global _initialized
    if _initialized:
        return
    cred_path = os.getenv("FIREBASE_CREDENTIALS", "credentials.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    _initialized = True


def get_db():
    _initialize()
    return firestore.client()
