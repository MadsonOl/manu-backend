import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from app.schemas.ordem_servico import OrdemServicoResponse
from app.firebase import get_db
from app.dependencies import get_current_user
from app.utils.empresas import carregar_empresas

router = APIRouter(prefix="/relatorios", tags=["Relatorios"])
logger = logging.getLogger("manu")


def _parse_data(valor: str, campo: str) -> datetime:
    # Data malformada vem do cliente: e erro de requisicao (422), nao falha do
    # servidor (500). Sem este try, o ValueError caia no except generico.
    try:
        return datetime.strptime(valor, "%d/%m/%Y")
    except ValueError:
        raise HTTPException(status_code=422, detail=f"{campo} invalido, use o formato DD/MM/YYYY")


def _data_do_registro(registro: dict):
    # Registros legados podem ter data ausente ou em outro formato; nesse caso
    # devolvemos None para o filtro ignorar o registro, em vez de derrubar o
    # relatorio inteiro com um 500.
    try:
        return datetime.strptime(registro.get("data", ""), "%d/%m/%Y")
    except ValueError:
        return None


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
            dt_inicio = _parse_data(data_inicio, "data_inicio")
            resultados = [
                r for r in resultados
                if (d := _data_do_registro(r)) is not None and d >= dt_inicio
            ]

        if data_fim:
            dt_fim = _parse_data(data_fim, "data_fim")
            resultados = [
                r for r in resultados
                if (d := _data_do_registro(r)) is not None and d <= dt_fim
            ]

        # Resolve a empresa em lote (mesma forma da listagem de ordens), sobre o
        # subconjunto ja filtrado, para o relatorio nao devolver empresa=null.
        empresas = carregar_empresas(db, (r.get("empresa_id") for r in resultados))
        for r in resultados:
            empresa_id = r.get("empresa_id")
            r["empresa"] = empresas.get(empresa_id) if empresa_id else None

        return resultados
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar relatorio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
