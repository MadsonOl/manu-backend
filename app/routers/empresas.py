import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.empresa import EmpresaCreate, EmpresaResponse
from app.firebase import get_db
from app.dependencies import get_current_user
from app.repositories.crud import CrudRepository

router = APIRouter(prefix="/empresas", tags=["Empresas"])
logger = logging.getLogger("manu")

repo = CrudRepository("empresas", nao_encontrado="Empresa nao encontrada", excluido="Empresa deletada com sucesso")


@router.post(
    "",
    response_model=EmpresaResponse,
    status_code=201,
    summary="Cadastrar empresa",
    description="Cadastra uma nova empresa no sistema. Requer autenticacao de gestor."
)
async def criar_empresa(
    empresa: EmpresaCreate, user: dict = Depends(get_current_user)
):
    try:
        return repo.criar(get_db(), empresa.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar empresa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "",
    response_model=list[EmpresaResponse],
    summary="Listar empresas",
    description="Retorna todas as empresas cadastradas. Requer autenticacao."
)
async def listar_empresas(user: dict = Depends(get_current_user)):
    try:
        return repo.listar(get_db())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    summary="Buscar empresa por ID",
    description="Retorna os dados de uma empresa especifica. Requer autenticacao."
)
async def obter_empresa(empresa_id: str, user: dict = Depends(get_current_user)):
    try:
        return repo.obter(get_db(), empresa_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    summary="Atualizar empresa",
    description="Atualiza os dados de uma empresa existente. Requer autenticacao de gestor."
)
async def atualizar_empresa(
    empresa_id: str,
    empresa: EmpresaCreate,
    user: dict = Depends(get_current_user),
):
    try:
        return repo.atualizar(get_db(), empresa_id, empresa.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete(
    "/{empresa_id}",
    summary="Excluir empresa",
    description="Remove uma empresa permanentemente. Requer autenticacao de gestor."
)
async def deletar_empresa(empresa_id: str, user: dict = Depends(get_current_user)):
    try:
        return repo.excluir(get_db(), empresa_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
