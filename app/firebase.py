import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth

logger = logging.getLogger("manu")
_initialized = False


def _initialize():
    global _initialized
    if _initialized:
        return
    cred_path = os.getenv("FIREBASE_CREDENTIALS", "credentials.json")
    logger.info(f"Inicializando Firebase com credenciais: {cred_path}")
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _initialized = True
        logger.info("Firebase inicializado com sucesso")
    except Exception as e:
        logger.error(f"ERRO ao inicializar Firebase: {type(e).__name__}: {e}")
        raise


def get_db():
    _initialize()
    return firestore.client()
