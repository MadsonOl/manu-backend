import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.firebase import _initialize
from firebase_admin import auth

logger = logging.getLogger("manu")
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    _initialize()
    token = credentials.credentials
    logger.info(f"Verificando token (primeiros 20 chars): {token[:20]}...")
    try:
        decoded = auth.verify_id_token(token)
        logger.info(f"Token valido para: {decoded.get('email', decoded.get('uid'))}")
        return decoded
    except Exception as e:
        logger.error(f"FALHA ao verificar token: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
        )
