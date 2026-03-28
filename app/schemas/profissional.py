from pydantic import BaseModel
from typing import Optional


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


class ProfissionalResponse(ProfissionalBase):
    id: str
