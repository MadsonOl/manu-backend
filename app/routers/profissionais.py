import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.profissional import ProfissionalCreate, ProfissionalResponse
from app.firebase import get_db
from app.dependencies import get_current_user
from app.repositories.crud import CrudRepository

router = APIRouter(prefix="/profissionais", tags=["Profissionais"])
logger = logging.getLogger("manu")

repo = CrudRepository("profissionais", nao_encontrado="Profissional nao encontrado", excluido="Profissional deletado com sucesso")


@router.post(
    "",
    response_model=ProfissionalResponse,
    status_code=201,
    summary="Cadastrar profissional",
    description="Cadastra um novo profissional no sistema. Requer autenticacao de gestor."
)
async def criar_profissional(
    profissional: ProfissionalCreate, user: dict = Depends(get_current_user)
):
    try:
        return repo.criar(get_db(), profissional.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar profissional: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "",
    response_model=list[ProfissionalResponse],
    summary="Listar profissionais",
    description="Retorna todos os profissionais cadastrados. Requer autenticacao."
)
async def listar_profissionais(user: dict = Depends(get_current_user)):
    try:
        return repo.listar(get_db())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar profissionais: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{profissional_id}",
    response_model=ProfissionalResponse,
    summary="Buscar profissional por ID",
    description="Retorna os dados de um profissional especifico. Requer autenticacao."
)
async def obter_profissional(
    profissional_id: str, user: dict = Depends(get_current_user)
):
    try:
        return repo.obter(get_db(), profissional_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put(
    "/{profissional_id}",
    response_model=ProfissionalResponse,
    summary="Atualizar profissional",
    description="Atualiza os dados de um profissional existente. Requer autenticacao de gestor."
)
async def atualizar_profissional(
    profissional_id: str,
    profissional: ProfissionalCreate,
    user: dict = Depends(get_current_user),
):
    try:
        return repo.atualizar(get_db(), profissional_id, profissional.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete(
    "/{profissional_id}",
    summary="Excluir profissional",
    description="Remove um profissional permanentemente. Requer autenticacao de gestor."
)
async def deletar_profissional(
    profissional_id: str, user: dict = Depends(get_current_user)
):
    try:
        return repo.excluir(get_db(), profissional_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar profissional {profissional_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
