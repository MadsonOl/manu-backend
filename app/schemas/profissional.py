from pydantic import BaseModel, field_validator
from typing import Optional

from app.schemas._validators import (
    texto,
    cpf as validar_cpf,
    telefone as validar_telefone,
    email as validar_email,
)


class ProfissionalBase(BaseModel):
    nome: str
    telefone: str
    email: str
    rg: str
    cpf: str
    funcao: Optional[str] = None
    funcao_id: Optional[str] = None


class ProfissionalCreate(ProfissionalBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Carlos Eduardo Santos",
                "telefone": "(11) 98765-4321",
                "email": "carlos.santos@email.com",
                "rg": "12.345.678-9",
                "cpf": "123.456.789-00",
                "funcao": "Eletricista"
            }
        }
    }

    @field_validator("nome", "rg")
    @classmethod
    def _obrigatorios(cls, v):
        return texto(v, maximo=200)

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, v):
        return validar_cpf(v)

    @field_validator("telefone")
    @classmethod
    def _telefone(cls, v):
        return validar_telefone(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return validar_email(v)


class ProfissionalResponse(ProfissionalBase):
    id: str
