import logging

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.schemas.chamado import ChamadoCreate, ChamadoResponse
from app.firebase import get_db
from app.dependencies import get_current_user
from app.repositories.crud import CrudRepository

router = APIRouter(prefix="/chamados", tags=["Chamados"])
logger = logging.getLogger("manu")

repo = CrudRepository("chamados", nao_encontrado="Chamado nao encontrado", excluido="Chamado deletado com sucesso")


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
        data = chamado.model_dump()
        # A data de abertura e definida pelo servidor (nao vem do cliente).
        data["data"] = datetime.now().strftime("%d/%m/%Y")
        return repo.criar(get_db(), data)
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
        return repo.listar(get_db())
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
        return repo.obter(get_db(), chamado_id)
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
        return repo.atualizar(get_db(), chamado_id, chamado.model_dump())
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
        return repo.excluir(get_db(), chamado_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar chamado {chamado_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
