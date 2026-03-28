import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.empresa import EmpresaCreate, EmpresaResponse
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/empresas", tags=["Empresas"])
logger = logging.getLogger("manu")


@router.post("", response_model=EmpresaResponse, status_code=201)
async def criar_empresa(
    empresa: EmpresaCreate, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        data = empresa.model_dump()
        doc_ref = db.collection("empresas").document()
        data["id"] = doc_ref.id
        doc_ref.set(data)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar empresa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("", response_model=list[EmpresaResponse])
async def listar_empresas(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection("empresas").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obter_empresa(empresa_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc = db.collection("empresas").document(empresa_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Empresa nao encontrada")
        return {"id": doc.id, **doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(
    empresa_id: str,
    empresa: EmpresaCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        doc_ref = db.collection("empresas").document(empresa_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Empresa nao encontrada")
        data = empresa.model_dump()
        doc_ref.update(data)
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{empresa_id}")
async def deletar_empresa(empresa_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc_ref = db.collection("empresas").document(empresa_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Empresa nao encontrada")
        doc_ref.delete()
        return {"message": "Empresa deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
