import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_current_user


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def autenticado():
    """Sobrescreve a verificacao de token para testar endpoints protegidos sem
    depender do Firebase."""
    app.dependency_overrides[get_current_user] = lambda: {"uid": "test", "email": "gestor@test"}
    yield
    app.dependency_overrides.pop(get_current_user, None)


def _mock_db_com(documentos=None, existe=True, dados=None):
    """Cria um mock do Firestore: collection().stream()/document().get()."""
    db = MagicMock()
    colecao = MagicMock()
    if documentos is not None:
        colecao.stream.return_value = documentos
    doc = MagicMock()
    doc.exists = existe
    doc.id = (dados or {}).get("id", "id-1")
    doc.to_dict.return_value = dados or {}
    docref = MagicMock()
    docref.get.return_value = doc
    colecao.document.return_value = docref
    db.collection.return_value = colecao
    return db


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


# ── CRUD autenticado (DB mockado) ─────────────────────────


@pytest.mark.asyncio
async def test_listar_empresas_autenticado_mapeia_id(client, autenticado):
    doc = MagicMock()
    doc.id = "2026-01-0001"
    doc.to_dict.return_value = {
        "cnpj": "11222333000181",
        "nome": "Acme",
        "endereco": "Rua 1",
        "gestor_manutencao": "Ana",
    }
    db = MagicMock()
    db.collection.return_value.stream.return_value = [doc]

    with patch("app.routers.empresas.get_db", return_value=db):
        async with client as c:
            response = await c.get("/empresas")

    assert response.status_code == 200
    corpo = response.json()
    assert corpo[0]["id"] == "2026-01-0001"
    assert corpo[0]["nome"] == "Acme"


@pytest.mark.asyncio
async def test_obter_empresa_inexistente_retorna_404(client, autenticado):
    db = _mock_db_com(existe=False)
    with patch("app.routers.empresas.get_db", return_value=db):
        async with client as c:
            response = await c.get("/empresas/nao-existe")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_excluir_empresa_existente_retorna_200(client, autenticado):
    db = _mock_db_com(existe=True, dados={"id": "e1"})
    with patch("app.routers.empresas.get_db", return_value=db):
        async with client as c:
            response = await c.delete("/empresas/e1")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_finalizar_os_inexistente_retorna_404(client, autenticado):
    db = _mock_db_com(existe=False)
    with patch("app.routers.ordens_servico.get_db", return_value=db):
        async with client as c:
            response = await c.patch("/ordens-servico/nao-existe/finalizar")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_criar_empresa_cnpj_invalido_autenticado_retorna_422(client, autenticado):
    # Mesmo autenticado, a validacao de schema (CNPJ invalido) deve barrar com 422
    # — e o handler deve responder 422 (e nao 500), regressao do bug de
    # serializacao do erro de validacao.
    payload = {
        "cnpj": "11222333000100",
        "nome": "Acme",
        "endereco": "Rua 1",
        "gestor_manutencao": "Ana",
    }
    async with client as c:
        response = await c.post("/empresas", json=payload)
    assert response.status_code == 422
