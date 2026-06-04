from pydantic import BaseModel, field_validator
from typing import Optional

from app.schemas._validators import texto, texto_opcional, cnpj as validar_cnpj


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

    @field_validator("nome", "endereco", "gestor_manutencao")
    @classmethod
    def _obrigatorios(cls, v):
        return texto(v, maximo=300)

    @field_validator("cnpj")
    @classmethod
    def _cnpj(cls, v):
        return validar_cnpj(v)

    @field_validator("informacoes_adicionais")
    @classmethod
    def _info(cls, v):
        return texto_opcional(v, maximo=2000)


class EmpresaResponse(EmpresaBase):
    id: str
