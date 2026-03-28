from pydantic import BaseModel
from typing import Optional


class EmpresaBase(BaseModel):
    cnpj: str
    nome: str
    endereco: str
    gestor_manutencao: str
    informacoes_adicionais: Optional[str] = None


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaResponse(EmpresaBase):
    id: str
