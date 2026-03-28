import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from app.schemas.ordem_servico import OrdemServicoResponse
from app.firebase import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/relatorios", tags=["Relatorios"])
logger = logging.getLogger("manu")


@router.get(
    "",
    response_model=list[OrdemServicoResponse],
    summary="Gerar relatorio de ordens de servico",
    description="""
Retorna lista de ordens de servico com filtros opcionais.
Todos os parametros de query sao opcionais e podem ser combinados.
Formato de data: DD/MM/YYYY
    """
)
async def listar_relatorios(
    profissional_id: Optional[str] = Query(None),
    data_inicio: Optional[str] = Query(None, description="Formato DD/MM/YYYY"),
    data_fim: Optional[str] = Query(None, description="Formato DD/MM/YYYY"),
    local: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        docs = db.collection("ordens_servico").stream()
        resultados = [{"id": doc.id, **doc.to_dict()} for doc in docs]

        if profissional_id:
            resultados = [r for r in resultados if r.get("responsavel") == profissional_id]

        if status:
            resultados = [r for r in resultados if r.get("status") == status]

        if local:
            resultados = [r for r in resultados if local.lower() in r.get("local", "").lower()]

        if data_inicio:
            dt_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
            resultados = [
                r for r in resultados
                if datetime.strptime(r.get("data", ""), "%d/%m/%Y") >= dt_inicio
            ]

        if data_fim:
            dt_fim = datetime.strptime(data_fim, "%d/%m/%Y")
            resultados = [
                r for r in resultados
                if datetime.strptime(r.get("data", ""), "%d/%m/%Y") <= dt_fim
            ]

        return resultados
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar relatorio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
