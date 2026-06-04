from pydantic import BaseModel, field_validator

from app.schemas._validators import texto


class FuncaoBase(BaseModel):
    nome: str


class FuncaoCreate(FuncaoBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Eletricista"
            }
        }
    }

    @field_validator("nome")
    @classmethod
    def _nome(cls, v):
        return texto(v, maximo=100)


class FuncaoResponse(FuncaoBase):
    id: str
