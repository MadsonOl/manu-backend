import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth

logger = logging.getLogger("manu")
_initialized = False


def _initialize():
    global _initialized
    if _initialized:
        return
    firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if firebase_json:
        cred_dict = json.loads(firebase_json)
        logger.info("Inicializando Firebase com credenciais via FIREBASE_CREDENTIALS_JSON")
    else:
        cred_dict = os.getenv("FIREBASE_CREDENTIALS", "credentials.json")
        logger.info(f"Inicializando Firebase com credenciais: {cred_dict}")
    try:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        _initialized = True
        logger.info("Firebase inicializado com sucesso")
    except Exception as e:
        logger.error(f"ERRO ao inicializar Firebase: {type(e).__name__}: {e}")
        raise


def get_db():
    _initialize()
    return firestore.client()
