import pytest
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
    async with client as c:
        response = await c.post("/chamados", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["local"] == payload["local"]
    assert "id" in data


@pytest.mark.asyncio
async def test_listar_profissionais_sem_token_retorna_401(client):
    async with client as c:
        response = await c.get("/profissionais")
    assert response.status_code in (401, 403)
