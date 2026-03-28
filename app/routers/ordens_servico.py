import logging

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.schemas.ordem_servico import OrdemServicoCreate, OrdemServicoResponse, StatusOS
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Servico"])
logger = logging.getLogger("manu")

COLLECTION = "ordens_servico"


@router.post("", response_model=OrdemServicoResponse, status_code=201)
async def criar_ordem_servico(
    os: OrdemServicoCreate, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        data = os.model_dump()
        data["data"] = datetime.now().strftime("%d/%m/%Y")
        doc_ref = db.collection(COLLECTION).document()
        data["id"] = doc_ref.id
        doc_ref.set(data)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar ordem de servico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("", response_model=list[OrdemServicoResponse])
async def listar_ordens_servico(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection(COLLECTION).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar ordens de servico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def obter_ordem_servico(os_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc = db.collection(COLLECTION).document(os_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Ordem de servico nao encontrada")
        return {"id": doc.id, **doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_ordem_servico(
    os_id: str,
    os: OrdemServicoCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        doc_ref = db.collection(COLLECTION).document(os_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Ordem de servico nao encontrada")
        data = os.model_dump()
        doc_ref.update(data)
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch("/{os_id}/finalizar", response_model=OrdemServicoResponse)
async def finalizar_ordem_servico(
    os_id: str, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        doc_ref = db.collection(COLLECTION).document(os_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Ordem de servico nao encontrada")
        doc_ref.update({"status": StatusOS.FINALIZADO.value})
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{os_id}")
async def deletar_ordem_servico(
    os_id: str, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        doc_ref = db.collection(COLLECTION).document(os_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Ordem de servico nao encontrada")
        doc_ref.delete()
        return {"message": "Ordem de servico deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
