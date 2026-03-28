# manu — Sistema de Gestao de Manutencoes

Plataforma web para gestao de chamados de manutencao, ordens de servico e profissionais. O backend expoe uma API REST que permite criar, listar, atualizar e remover recursos como chamados, ordens de servico, empresas, profissionais e funcoes, alem de gerar relatorios filtrados.

## Tecnologias Utilizadas

- Python 3.13
- FastAPI
- Firebase Admin SDK (Firestore + Firebase Auth)
- Pydantic (validacao de dados)
- Docker e Docker Compose
- Uvicorn
- Pytest + pytest-cov
- GitHub Actions (CI/CD)
- Render (deploy)

## Como Rodar Localmente

### Pre-requisitos

- Python 3.13
- Docker Desktop (opcional, para rodar via container)
- Arquivo `credentials.json` com as credenciais de servico do Firebase Admin SDK

### Opcao 1 — Python + venv

```bash
# Clonar o repositorio
git clone https://github.com/MadsonOl/manu-frontend-.git
cd manu-backend

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Edite o arquivo .env e coloque o caminho do seu credentials.json

# Rodar a aplicacao
uvicorn app.main:app --reload
```

A API estara disponivel em `http://localhost:8000`.

### Opcao 2 — Docker Compose

```bash
# Clonar o repositorio
git clone https://github.com/MadsonOl/manu-frontend-.git
cd manu-backend

# Configurar variaveis de ambiente
cp .env.example .env

# Coloque o arquivo credentials.json na raiz do projeto

# Subir os containers
docker-compose up --build
```

## Documentacao Interativa (Swagger)

Com a aplicacao rodando, acesse a documentacao interativa da API em:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

A documentacao permite testar os endpoints diretamente pelo navegador.

## Variaveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (ou copie de `.env.example`):

| Variavel | Descricao | Valor padrao |
|----------|-----------|--------------|
| `FIREBASE_CREDENTIALS` | Caminho para o arquivo `credentials.json` com as credenciais de servico do Firebase Admin SDK | `credentials.json` |

### Secrets do GitHub Actions

Para o pipeline de CI/CD funcionar, configure o seguinte secret no repositorio GitHub:

| Secret | Descricao |
|--------|-----------|
| `RENDER_DEPLOY_HOOK_URL` | URL do Deploy Hook fornecida pelo Render |

## Estrutura de Pastas

```
manu-backend/
├── app/
│   ├── main.py              # Entrypoint da aplicacao (CORS, middleware, rotas)
│   ├── firebase.py          # Inicializacao do Firebase e cliente Firestore
│   ├── dependencies.py      # Autenticacao (verificacao de token JWT Firebase)
│   ├── routers/             # Rotas da API
│   │   ├── chamados.py
│   │   ├── ordens_servico.py
│   │   ├── profissionais.py
│   │   ├── empresas.py
│   │   ├── funcoes.py
│   │   └── relatorios.py
│   ├── schemas/             # Modelos Pydantic (validacao de dados)
│   │   ├── chamado.py
│   │   ├── ordem_servico.py
│   │   ├── profissional.py
│   │   ├── empresa.py
│   │   └── funcao.py
│   └── utils/
│       └── id_generator.py  # Gerador de IDs sequenciais (formato YYYY-MM-XXXX)
├── tests/
│   └── test_main.py         # Testes automatizados
├── .github/
│   └── workflows/
│       └── deploy.yml        # Pipeline CI/CD (testes + deploy)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Autenticacao

A API utiliza **Firebase Authentication** com tokens JWT.

**Fluxo:**
1. O cliente se autentica via Firebase Auth (externo a esta API)
2. Firebase retorna um ID Token (JWT)
3. O cliente envia o token no header: `Authorization: Bearer <token>`
4. A API valida o token usando o Firebase Admin SDK

**Endpoints publicos (sem autenticacao):**
- `POST /chamados` — abertura de chamado por usuario externo
- `GET /` — status da API

Todos os demais endpoints exigem token valido.

## Endpoints

### Root

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| GET | `/` | Health check — retorna `{"status": "online"}` | Nao |

### Chamados

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| POST | `/chamados` | Criar novo chamado | Nao |
| GET | `/chamados` | Listar todos os chamados | Sim |
| GET | `/chamados/{chamado_id}` | Buscar chamado por ID | Sim |
| PUT | `/chamados/{chamado_id}` | Atualizar chamado | Sim |
| DELETE | `/chamados/{chamado_id}` | Remover chamado | Sim |

### Ordens de Servico

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| POST | `/ordens-servico` | Criar nova ordem de servico | Sim |
| GET | `/ordens-servico` | Listar todas as ordens | Sim |
| GET | `/ordens-servico/{os_id}` | Buscar ordem por ID | Sim |
| PUT | `/ordens-servico/{os_id}` | Atualizar ordem | Sim |
| PATCH | `/ordens-servico/{os_id}/finalizar` | Finalizar ordem de servico | Sim |
| DELETE | `/ordens-servico/{os_id}` | Remover ordem | Sim |

### Profissionais

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| POST | `/profissionais` | Cadastrar novo profissional | Sim |
| GET | `/profissionais` | Listar todos os profissionais | Sim |
| GET | `/profissionais/{profissional_id}` | Buscar profissional por ID | Sim |
| PUT | `/profissionais/{profissional_id}` | Atualizar profissional | Sim |
| DELETE | `/profissionais/{profissional_id}` | Remover profissional | Sim |

### Empresas

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| POST | `/empresas` | Cadastrar nova empresa | Sim |
| GET | `/empresas` | Listar todas as empresas | Sim |
| GET | `/empresas/{empresa_id}` | Buscar empresa por ID | Sim |
| PUT | `/empresas/{empresa_id}` | Atualizar empresa | Sim |
| DELETE | `/empresas/{empresa_id}` | Remover empresa | Sim |

### Funcoes

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| POST | `/funcoes` | Criar nova funcao | Sim |
| GET | `/funcoes` | Listar todas as funcoes | Sim |
| GET | `/funcoes/{funcao_id}` | Buscar funcao por ID | Sim |
| PUT | `/funcoes/{funcao_id}` | Atualizar funcao | Sim |
| DELETE | `/funcoes/{funcao_id}` | Remover funcao | Sim |

### Relatorios

| Metodo | Rota | Descricao | Autenticacao |
|--------|------|-----------|--------------|
| GET | `/relatorios` | Gerar relatorio filtrado de ordens de servico | Sim |

Parametros de query opcionais para `/relatorios`:

| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| `profissional_id` | string | Filtrar por ID do profissional |
| `data_inicio` | string | Data inicial (formato DD/MM/AAAA) |
| `data_fim` | string | Data final (formato DD/MM/AAAA) |
| `local` | string | Filtrar por local (busca parcial, case-insensitive) |
| `status` | string | Filtrar por status (`EM_ATENDIMENTO` ou `FINALIZADO`) |

## Schemas das Entidades

Todos os IDs sao gerados automaticamente no formato `YYYY-MM-XXXX` (ex: `2026-03-0001`), com contador sequencial mensal.

### Chamado

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | auto | ID gerado automaticamente |
| `local` | string | sim | Local da ocorrencia |
| `descricao` | string | sim | Descricao do problema |
| `prioridade` | enum | nao | `BAIXA`, `NORMAL` (padrao) ou `ALTA` |
| `solicitante` | string | sim | Nome do solicitante |
| `data` | string | auto | Data de criacao (DD/MM/AAAA) |

### Ordem de Servico

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | auto | ID gerado automaticamente |
| `local` | string | sim | Local do servico |
| `descricao` | string | sim | Descricao do servico |
| `prioridade` | enum | nao | `BAIXA`, `NORMAL` (padrao) ou `ALTA` |
| `solicitante` | string | sim | Nome do solicitante |
| `responsavel` | string | nao | Responsavel pela ordem |
| `profissional` | string | nao | Nome do profissional atribuido |
| `status` | enum | nao | `EM_ATENDIMENTO` (padrao) ou `FINALIZADO` |
| `empresa_id` | string | nao | ID da empresa vinculada |
| `chamado_id` | string | nao | ID do chamado de origem |
| `data` | string | auto | Data de criacao (DD/MM/AAAA) |

### Profissional

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | auto | ID gerado automaticamente |
| `nome` | string | sim | Nome completo |
| `telefone` | string | sim | Telefone de contato |
| `email` | string | sim | E-mail |
| `rg` | string | sim | Documento RG |
| `cpf` | string | sim | Documento CPF |
| `funcao` | string | nao | Nome da funcao exercida |
| `funcao_id` | string | nao | ID da funcao vinculada |

### Empresa

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | auto | ID gerado automaticamente |
| `cnpj` | string | sim | CNPJ da empresa |
| `nome` | string | sim | Razao social |
| `endereco` | string | sim | Endereco completo |
| `gestor_manutencao` | string | sim | Nome do gestor de manutencao |
| `informacoes_adicionais` | string | nao | Observacoes adicionais |

### Funcao

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | string | auto | ID gerado automaticamente |
| `nome` | string | sim | Nome da funcao (ex: Eletricista) |

## CORS

A API permite requisicoes dos seguintes dominios:

- **Desenvolvimento local:** `http://localhost:5173` ate `http://localhost:5180` (e equivalentes em `127.0.0.1`)
- **Producao:** `https://manu-frontend-beta.vercel.app`

## Como Rodar os Testes

```bash
# Rodar testes
pytest tests/ -v

# Rodar testes com relatorio de cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Deploy

- **Plataforma:** Render
- **CI/CD:** GitHub Actions com pipeline automatico no push para `main`
  - Job `test` — roda os testes com pytest e gera relatorio de cobertura
  - Job `deploy` — aciona o deploy no Render via Deploy Hook (requer secret `RENDER_DEPLOY_HOOK_URL`)

## Fluxo Principal

1. Usuario externo abre um chamado via link publico (`POST /chamados`, sem autenticacao)
2. Gestor se autentica via Firebase Auth
3. Gestor visualiza os chamados e converte em ordem de servico
4. Gestor atribui a ordem a um profissional cadastrado
5. Profissional executa o servico de manutencao
6. Gestor finaliza a ordem (`PATCH /ordens-servico/{id}/finalizar`)
7. Relatorios filtrados ficam disponiveis para consulta e impressao

## Licenca

MIT
