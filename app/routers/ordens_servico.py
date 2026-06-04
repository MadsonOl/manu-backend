import logging

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.schemas.ordem_servico import OrdemServicoCreate, OrdemServicoResponse, StatusOS
from app.firebase import get_db
from app.dependencies import get_current_user
from app.utils.id_generator import gerar_id
from app.utils.empresas import carregar_empresas
from app.repositories.crud import CrudRepository

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Servico"])
logger = logging.getLogger("manu")

COLLECTION = "ordens_servico"

# Reaproveita o CRUD generico nas operacoes de item unico. A listagem, a criacao
# e o finalizar permanecem proprios por causa da resolucao de empresa em lote e
# das regras especificas (data, responsavel, status).
repo = CrudRepository(COLLECTION, nao_encontrado="Ordem de servico nao encontrada", excluido="Ordem de servico deletada com sucesso")


def _resolve_empresa(db, os_data: dict) -> dict:
    empresa_id = os_data.get("empresa_id")
    if empresa_id:
        doc = db.collection("empresas").document(empresa_id).get()
        if doc.exists:
            os_data["empresa"] = {"id": doc.id, **doc.to_dict()}
        else:
            os_data["empresa"] = None
    else:
        os_data["empresa"] = None
    return os_data


@router.post(
    "",
    response_model=OrdemServicoResponse,
    status_code=201,
    summary="Criar ordem de servico",
    description="Cria uma nova ordem de servico a partir de um chamado. Requer autenticacao de gestor."
)
async def criar_ordem_servico(
    os: OrdemServicoCreate, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        data = os.model_dump()
        data["data"] = datetime.now().strftime("%d/%m/%Y")

        if data.get("profissional") and not data.get("responsavel"):
            data["responsavel"] = data["profissional"]

        data = {k: v for k, v in data.items() if v is not None}

        novo_id = gerar_id("ordens_servico")
        doc_ref = db.collection(COLLECTION).document(novo_id)
        data["id"] = novo_id
        doc_ref.set(data)

        return_data = {
            "id": novo_id,
            "data": data["data"],
            "local": data.get("local", ""),
            "descricao": data.get("descricao", ""),
            "prioridade": data.get("prioridade", "NORMAL"),
            "solicitante": data.get("solicitante", ""),
            "responsavel": data.get("responsavel"),
            "profissional": data.get("profissional"),
            "status": data.get("status", "EM_ATENDIMENTO"),
            "empresa_id": data.get("empresa_id"),
            "chamado_id": data.get("chamado_id"),
        }
        return _resolve_empresa(db, return_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar ordem de servico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "",
    response_model=list[OrdemServicoResponse],
    summary="Listar ordens de servico",
    description="Retorna todas as ordens de servico cadastradas. Requer autenticacao."
)
async def listar_ordens_servico(user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        docs = db.collection(COLLECTION).stream()
        resultado = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        # Resolve as empresas em lote e preenche em memoria (mesma forma de
        # _resolve_empresa: dict {id, ...} quando existe, None caso contrario).
        empresas = carregar_empresas(db, (item.get("empresa_id") for item in resultado))
        for item in resultado:
            empresa_id = item.get("empresa_id")
            item["empresa"] = empresas.get(empresa_id) if empresa_id else None
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar ordens de servico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/{os_id}",
    response_model=OrdemServicoResponse,
    summary="Buscar ordem de servico por ID",
    description="Retorna os dados de uma ordem de servico especifica. Requer autenticacao."
)
async def obter_ordem_servico(os_id: str, user: dict = Depends(get_current_user)):
    try:
        db = get_db()
        return _resolve_empresa(db, repo.obter(db, os_id))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put(
    "/{os_id}",
    response_model=OrdemServicoResponse,
    summary="Atualizar ordem de servico",
    description="Atualiza os dados de uma ordem de servico existente. Requer autenticacao."
)
async def atualizar_ordem_servico(
    os_id: str,
    os: OrdemServicoCreate,
    user: dict = Depends(get_current_user),
):
    try:
        db = get_db()
        # Resolve a empresa como em GET/POST, para o PUT nao devolver empresa=null.
        return _resolve_empresa(db, repo.atualizar(db, os_id, os.model_dump()))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.patch(
    "/{os_id}/finalizar",
    response_model=OrdemServicoResponse,
    summary="Finalizar ordem de servico",
    description="Muda o status da OS para FINALIZADO. Requer autenticacao."
)
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


@router.delete(
    "/{os_id}",
    summary="Excluir ordem de servico",
    description="Remove uma ordem de servico permanentemente. Requer autenticacao."
)
async def deletar_ordem_servico(
    os_id: str, user: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        return repo.excluir(db, os_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar ordem de servico {os_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
