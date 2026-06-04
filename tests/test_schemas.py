"""Testes da validacao de entrada (schemas Create). Nao dependem de rede nem do
Firebase: apenas instanciam os modelos Pydantic."""
import pytest
from pydantic import ValidationError

from app.schemas.chamado import ChamadoCreate
from app.schemas.empresa import EmpresaCreate
from app.schemas.profissional import ProfissionalCreate
from app.schemas.funcao import FuncaoCreate


# ── Chamado ───────────────────────────────────────────────

def test_chamado_valido():
    c = ChamadoCreate(local="  Bloco B  ", descricao="Vazamento", solicitante="Maria")
    assert c.local == "Bloco B"  # normaliza (strip)


@pytest.mark.parametrize("campo", ["local", "descricao", "solicitante"])
def test_chamado_campo_em_branco(campo):
    base = {"local": "B", "descricao": "D", "solicitante": "S"}
    base[campo] = "   "
    with pytest.raises(ValidationError):
        ChamadoCreate(**base)


def test_chamado_descricao_muito_longa():
    with pytest.raises(ValidationError):
        ChamadoCreate(local="B", descricao="x" * 2001, solicitante="S")


# ── Empresa ───────────────────────────────────────────────

def test_empresa_cnpj_valido_normaliza_para_digitos():
    e = EmpresaCreate(
        cnpj="11.222.333/0001-81",
        nome="Acme",
        endereco="Rua 1",
        gestor_manutencao="Ana",
    )
    assert e.cnpj == "11222333000181"


def test_empresa_cnpj_invalido():
    with pytest.raises(ValidationError):
        EmpresaCreate(cnpj="11222333000100", nome="Acme", endereco="Rua 1", gestor_manutencao="Ana")


# ── Profissional ──────────────────────────────────────────

def test_profissional_valido_normaliza_documentos():
    p = ProfissionalCreate(
        nome="Carlos",
        telefone="(11) 98888-7777",
        email="carlos@x.com",
        rg="123456789",
        cpf="529.982.247-25",
    )
    assert p.cpf == "52998224725"
    assert p.telefone == "11988887777"


@pytest.mark.parametrize("campo,valor", [
    ("cpf", "12345678900"),       # DV invalido
    ("telefone", "999"),           # curto demais
    ("email", "sem-arroba"),       # formato invalido
    ("nome", "   "),               # vazio
])
def test_profissional_invalido(campo, valor):
    base = {
        "nome": "Carlos",
        "telefone": "11988887777",
        "email": "carlos@x.com",
        "rg": "123456789",
        "cpf": "52998224725",
    }
    base[campo] = valor
    with pytest.raises(ValidationError):
        ProfissionalCreate(**base)


# ── Funcao ────────────────────────────────────────────────

def test_funcao_em_branco():
    with pytest.raises(ValidationError):
        FuncaoCreate(nome="  ")
