from pydantic import BaseModel
from typing import Optional


class EmpresaBase(BaseModel):
    cnpj: str
    nome: str
    endereco: str
    gestor_manutencao: str
    informacoes_adicionais: Optional[str] = None


class EmpresaCreate(EmpresaBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "cnpj": "12.345.678/0001-90",
                "nome": "Predial Manutencoes Ltda",
                "endereco": "Rua das Flores, 100 - Centro",
                "gestor_manutencao": "Ana Paula Oliveira",
                "informacoes_adicionais": "Contrato vigente ate 12/2026"
            }
        }
    }


class EmpresaResponse(EmpresaBase):
    id: str
