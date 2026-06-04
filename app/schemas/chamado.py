from pydantic import BaseModel, field_validator
from enum import Enum

from app.schemas._validators import texto


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

    # Validacao de entrada (endpoint publico): exige textos nao-vazios e limita
    # o tamanho para evitar abuso. Aplicada so no Create, nao no Response.
    @field_validator("local", "solicitante")
    @classmethod
    def _curtos(cls, v):
        return texto(v, maximo=200)

    @field_validator("descricao")
    @classmethod
    def _descricao(cls, v):
        return texto(v, maximo=2000)


class ChamadoResponse(ChamadoBase):
    id: str
    data: str
