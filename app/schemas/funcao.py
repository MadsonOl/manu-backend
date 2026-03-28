from pydantic import BaseModel


class FuncaoBase(BaseModel):
    nome: str


class FuncaoCreate(FuncaoBase):
    pass


class FuncaoResponse(FuncaoBase):
    id: str
