from pydantic import BaseModel


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


class FuncaoResponse(FuncaoBase):
    id: str
