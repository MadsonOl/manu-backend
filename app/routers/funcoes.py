import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.funcao import FuncaoCreate, FuncaoResponse
from app.firebase import get_db
from app.dependencies import get_current_user
from app.repositories.crud import CrudRepository

router = APIRouter(prefix="/funcoes", tags=["Funcoes"])
logger = logging.getLogger("manu")

repo = CrudRepository("funcoes", nao_encontrado="Funcao nao encontrada", excluido="Funcao deletada com sucesso")


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
        return repo.criar(get_db(), funcao.model_dump())
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
        return repo.listar(get_db())
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
        return repo.obter(get_db(), funcao_id)
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
        return repo.atualizar(get_db(), funcao_id, funcao.model_dump())
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
        return repo.excluir(get_db(), funcao_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar funcao {funcao_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
