from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum
from app.schemas.chamado import Prioridade
from app.schemas._validators import texto


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

    @field_validator("local", "solicitante")
    @classmethod
    def _curtos(cls, v):
        return texto(v, maximo=200)

    @field_validator("descricao")
    @classmethod
    def _descricao(cls, v):
        return texto(v, maximo=2000)


class OrdemServicoResponse(OrdemServicoBase):
    id: str
    data: str
    empresa: Optional[dict] = None
