import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger("manu")
_initialized = False


def _initialize():
    global _initialized
    if _initialized:
        return
    # A credencial pode vir como JSON inline (FIREBASE_CREDENTIALS_JSON, usado no
    # deploy) ou como caminho de um arquivo (FIREBASE_CREDENTIALS, padrao local).
    # credentials.Certificate aceita tanto o dict quanto o caminho, por isso a
    # mesma variavel guarda as duas formas conforme a origem.
    firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if firebase_json:
        credencial = json.loads(firebase_json)
        logger.info("Inicializando Firebase com credenciais via FIREBASE_CREDENTIALS_JSON")
    else:
        credencial = os.getenv("FIREBASE_CREDENTIALS", "credentials.json")
        # Nao logar o caminho do arquivo de credencial (evita expor o layout do
        # deploy/segredos nos logs); apenas a origem.
        logger.info("Inicializando Firebase com credenciais via arquivo (FIREBASE_CREDENTIALS)")
    try:
        cred = credentials.Certificate(credencial)
        firebase_admin.initialize_app(cred)
        _initialized = True
        logger.info("Firebase inicializado com sucesso")
    except Exception as e:
        logger.error(f"ERRO ao inicializar Firebase: {type(e).__name__}: {e}")
        raise


def get_db():
    _initialize()
    return firestore.client()
