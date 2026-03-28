import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.profissional import ProfissionalCreate, ProfissionalResponse
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/profissionais", tags=["Profissionais"])
logger = logging.getLogger("manu")


@router.post("", response_model=ProfissionalResponse, status_code=201)
async def criar_profissional(
    profissional: ProfissionalCreate, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        data = profissional.model_dump()
        doc_ref = db.collection("profissionais").document()
        data["id"] = doc_ref.id
        doc_ref.set(data)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar profissional: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("", response_model=list[ProfissionalResponse])
async def listar_profissionais(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection("profissionais").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar profissionais: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{profissional_id}", response_model=ProfissionalResponse)
async def obter_profissional(
    profissional_id: str, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        doc = db.collection("profissionais").document(profissional_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Profissional nao encontrado")
        return {"id": doc.id, **doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{profissional_id}", response_model=ProfissionalResponse)
async def atualizar_profissional(
    profissional_id: str,
    profissional: ProfissionalCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        doc_ref = db.collection("profissionais").document(profissional_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Profissional nao encontrado")
        data = profissional.model_dump()
        doc_ref.update(data)
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{profissional_id}")
async def deletar_profissional(
    profissional_id: str, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        doc_ref = db.collection("profissionais").document(profissional_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Profissional nao encontrado")
        doc_ref.delete()
        return {"message": "Profissional deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
