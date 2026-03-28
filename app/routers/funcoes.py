import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.funcao import FuncaoCreate, FuncaoResponse
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/funcoes", tags=["Funcoes"])
logger = logging.getLogger("manu")


@router.post(
    "",
    response_model=FuncaoResponse,
    status_code=201,
    summary="Cadastrar funcao",
    description="Cadastra uma nova funcao (cargo) no sistema. Requer autenticacao de gestor."
)
async def criar_funcao(
    funcao: FuncaoCreate, user: dict = Depends(get_current_user)
):
    try:
        from app.utils.id_generator import gerar_id
        db = get_db()
        data = funcao.model_dump()
        novo_id = gerar_id("funcoes")
        doc_ref = db.collection("funcoes").document(novo_id)
        data["id"] = novo_id
        doc_ref.set(data)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar funcao: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "",
    response_model=list[FuncaoResponse],
    summary="Listar funcoes",
    description="Retorna todas as funcoes cadastradas. Requer autenticacao."
)
async def listar_funcoes(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection("funcoes").stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar funcoes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{funcao_id}",
    response_model=FuncaoResponse,
    summary="Buscar funcao por ID",
    description="Retorna os dados de uma funcao especifica. Requer autenticacao."
)
async def obter_funcao(funcao_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc = db.collection("funcoes").document(funcao_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Funcao nao encontrada")
        return {"id": doc.id, **doc.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter funcao {funcao_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put(
    "/{funcao_id}",
    response_model=FuncaoResponse,
    summary="Atualizar funcao",
    description="Atualiza os dados de uma funcao existente. Requer autenticacao de gestor."
)
async def atualizar_funcao(
    funcao_id: str,
    funcao: FuncaoCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        doc_ref = db.collection("funcoes").document(funcao_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Funcao nao encontrada")
        data = funcao.model_dump()
        doc_ref.update(data)
        updated = doc_ref.get()
        return {"id": updated.id, **updated.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar funcao {funcao_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete(
    "/{funcao_id}",
    summary="Excluir funcao",
    description="Remove uma funcao permanentemente. Requer autenticacao de gestor."
)
async def deletar_funcao(funcao_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        doc_ref = db.collection("funcoes").document(funcao_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Funcao nao encontrada")
        doc_ref.delete()
        return {"message": "Funcao deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar funcao {funcao_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
