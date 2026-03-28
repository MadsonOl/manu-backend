import logging

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.schemas.chamado import ChamadoCreate, ChamadoResponse
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/chamados", tags=["Chamados"])
logger = logging.getLogger("manu")


@router.post(
    "",
    response_model=ChamadoResponse,
    status_code=201,
    summary="Abrir novo chamado",
    description="""
Endpoint publico — nao requer autenticacao.
Usado por usuarios externos via link ou QR Code para registrar
uma solicitacao de manutencao. O ID e a data sao gerados
automaticamente pelo servidor.
    """
)
async def criar_chamado(chamado: ChamadoCreate):
    try:
        db = get_db()
        data = chamado.model_dump()
        data["data"] = datetime.now().strftime("%d/%m/%Y")
        doc_ref = db.collection("chamados").document()
        data["id"] = doc_ref.id
        doc_ref.set(data)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar chamado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "",
    response_model=list[ChamadoResponse],
    summary="Listar todos os chamados",
    description="Retorna todos os chamados cadastrados. Requer autenticacao de gestor."
)
async def listar_chamados(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection("chamados").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar chamados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    summary="Buscar chamado por ID",
    description="Retorna os dados de um chamado especifico. Requer autenticacao de gestor."
)
async def obter_chamado(chamado_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc = db.collection("chamados").document(chamado_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        return {"id": doc.id, **doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter chamado {chamado_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put(
    "/{chamado_id}",
    response_model=ChamadoResponse,
    summary="Atualizar chamado",
    description="Atualiza os dados de um chamado existente. Requer autenticacao de gestor."
)
async def atualizar_chamado(
    chamado_id: str,
    chamado: ChamadoCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        doc_ref = db.collection("chamados").document(chamado_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        data = chamado.model_dump()
        doc_ref.update(data)
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar chamado {chamado_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete(
    "/{chamado_id}",
    summary="Excluir chamado",
    description="Remove um chamado permanentemente. Requer autenticacao de gestor."
)
async def deletar_chamado(chamado_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc_ref = db.collection("chamados").document(chamado_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Chamado nao encontrado")
        doc_ref.delete()
        return {"message": "Chamado deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar chamado {chamado_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
