from pydantic import BaseModel
from enum import Enum


class Prioridade(str, Enum):
    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"


class ChamadoBase(BaseModel):
    local: str
    descricao: str
    prioridade: Prioridade = Prioridade.NORMAL
    solicitante: str


class ChamadoCreate(ChamadoBase):
    pass


class ChamadoResponse(ChamadoBase):
    id: str
    data: str
