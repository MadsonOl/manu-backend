from pydantic import BaseModel
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
    responsavel: str
    status: StatusOS = StatusOS.EM_ATENDIMENTO
    empresa_id: str


class OrdemServicoCreate(OrdemServicoBase):
    pass


class OrdemServicoResponse(OrdemServicoBase):
    id: str
    data: str
