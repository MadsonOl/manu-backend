from pydantic import BaseModel
from typing import Optional
from enum import Enum
from app.schemas.chamado import Prioridade


class StatusOS(str, Enum):
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    FINALIZADO = "FINALIZADO"


class OrdemServicoBase(BaseModel):
    local: str
    descricao: str
    prioridade: Prioridade = Prioridade.NORMAL
    solicitante: str
    responsavel: Optional[str] = None
    profissional: Optional[str] = None
    status: StatusOS = StatusOS.EM_ATENDIMENTO
    empresa_id: Optional[str] = None
    chamado_id: Optional[str] = None


class OrdemServicoCreate(OrdemServicoBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "local": "Bloco A - Banheiro Masculino",
                "descricao": "Substituicao de lampadas queimadas",
                "prioridade": "NORMAL",
                "solicitante": "Joao Pereira",
                "profissional": "Carlos Eduardo Santos"
            }
        }
    }


class OrdemServicoResponse(OrdemServicoBase):
    id: str
    data: str
    empresa: Optional[dict] = None
