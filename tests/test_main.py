import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_root_retorna_200(client):
    async with client as c:
        response = await c.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


@pytest.mark.asyncio
async def test_criar_chamado_retorna_201(client):
    payload = {
        "local": "Bloco B - Sala 202",
        "descricao": "Vazamento no banheiro",
        "prioridade": "ALTA",
        "solicitante": "Joao Teste",
    }

    mock_doc = MagicMock()
    mock_collection = MagicMock()
    mock_collection.document.return_value = mock_doc
    mock_db = MagicMock()
    mock_db.collection.return_value = mock_collection

    with patch("app.routers.chamados.get_db", return_value=mock_db), \
         patch("app.utils.id_generator.gerar_id", return_value="2026-03-0001"):
        async with client as c:
            response = await c.post("/chamados", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["local"] == payload["local"]
    assert data["id"] == "2026-03-0001"


@pytest.mark.asyncio
async def test_listar_profissionais_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/profissionais")
    assert response.status_code in (401, 403)


# ── Chamados ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_criar_chamado_sem_local_retorna_422(client):
    payload = {
        "descricao": "Vazamento no banheiro",
        "prioridade": "ALTA",
        "solicitante": "Joao Teste",
    }
    async with client as c:
        response = await c.post("/chamados", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_chamado_prioridade_invalida_retorna_422(client):
    payload = {
        "local": "Bloco B - Sala 202",
        "descricao": "Vazamento no banheiro",
        "prioridade": "URGENTE",
        "solicitante": "Joao Teste",
    }
    async with client as c:
        response = await c.post("/chamados", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_chamado_local_em_branco_retorna_422(client):
    # Endpoint publico: campo so com espacos deve ser rejeitado pela validacao.
    payload = {
        "local": "   ",
        "descricao": "Vazamento no banheiro",
        "prioridade": "ALTA",
        "solicitante": "Joao Teste",
    }
    async with client as c:
        response = await c.post("/chamados", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_criar_chamado_descricao_muito_longa_retorna_422(client):
    payload = {
        "local": "Bloco B",
        "descricao": "x" * 2001,
        "prioridade": "ALTA",
        "solicitante": "Joao Teste",
    }
    async with client as c:
        response = await c.post("/chamados", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_listar_chamados_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/chamados")
    assert response.status_code in (401, 403)


# ── Ordens de Servico ────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_ordens_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/ordens-servico")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_finalizar_os_sem_token_retorna_401(client):
    async with client as c:
        response = await c.patch("/ordens-servico/id-qualquer/finalizar")
    assert response.status_code in (401, 403)


# ── Profissionais ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_criar_profissional_sem_token_retorna_401(client):
    # Payload valido (digitos), como o frontend envia, para o teste exercitar a
    # camada de autenticacao e nao a de validacao.
    payload = {
        "nome": "Carlos Eduardo",
        "telefone": "11987654321",
        "email": "carlos@email.com",
        "rg": "123456789",
        "cpf": "52998224725",
        "funcao_id": "abc123",
    }
    async with client as c:
        response = await c.post("/profissionais", json=payload)
    assert response.status_code in (401, 403)


# ── Empresas ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_empresas_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/empresas")
    assert response.status_code in (401, 403)


# ── Funcoes ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_funcoes_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/funcoes")
    assert response.status_code in (401, 403)


# ── Relatorios ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_relatorios_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/relatorios")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_relatorios_com_filtro_status_invalido(client):
    async with client as c:
        response = await c.get("/relatorios?status=INEXISTENTE")
    assert response.status_code in (401, 403)
