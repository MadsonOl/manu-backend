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
    model_config = {
        "json_schema_extra": {
            "example": {
                "local": "Bloco B - Sala 202",
                "descricao": "Torneira com vazamento continuo",
                "prioridade": "ALTA",
                "solicitante": "Maria Silva"
            }
        }
    }


class ChamadoResponse(ChamadoBase):
    id: str
    data: str
