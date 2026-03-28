from pydantic import BaseModel
from typing import Optional


class ProfissionalBase(BaseModel):
    nome: str
    telefone: str
    email: str
    rg: str
    cpf: str
    funcao_id: str


class ProfissionalCreate(ProfissionalBase):
    pass


class ProfissionalResponse(ProfissionalBase):
    id: str
