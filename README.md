# manu — Sistema de Gestao de Manutencoes

Plataforma web para gestao de chamados de manutencao, ordens de servico e profissionais. O backend expoe uma API REST que permite criar, listar, atualizar e remover recursos como chamados, ordens de servico, empresas, profissionais e funcoes, alem de gerar relatorios filtrados.

## Tecnologias Utilizadas

- Python 3.13
- FastAPI
- Firebase Admin SDK (Firestore + Firebase Auth)
- Docker e Docker Compose
- Uvicorn
- Pytest

## Como Rodar Localmente

### Pre-requisitos

- Python 3.13
- Docker Desktop (opcional, para rodar via container)

### Opcao 1 — Python + venv

```bash
# Clonar o repositorio
git clone https://github.com/seu-usuario/manu-backend.git
cd manu-backend

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais

# Rodar a aplicacao
uvicorn app.main:app --reload
```

A API estara disponivel em `http://localhost:8000`.

### Opcao 2 — Docker Compose

```bash
# Clonar o repositorio
git clone https://github.com/seu-usuario/manu-backend.git
cd manu-backend

# Configurar variaveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais

# Subir os containers
docker-compose up --build
```

## Variaveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variaveis:

| Variavel | Descricao |
|----------|-----------|
| `FIREBASE_CREDENTIALS` | Caminho para o arquivo `credentials.json` com as credenciais de servico do Firebase Admin SDK |

## Estrutura de Pastas

```
manu-backend/
├── app/
│   ├── main.py           # Entrypoint da aplicacao
│   ├── firebase.py       # Inicializacao do Firebase
│   ├── dependencies.py   # Autenticacao (verificacao de token Firebase)
│   ├── routers/          # Rotas da API
│   │   ├── chamados.py
│   │   ├── ordens_servico.py
│   │   ├── profissionais.py
│   │   ├── empresas.py
│   │   ├── funcoes.py
│   │   └── relatorios.py
│   ├── schemas/          # Modelos Pydantic (validacao de dados)
│   │   ├── chamado.py
│   │   ├── ordem_servico.py
│   │   ├── profissional.py
│   │   ├── empresa.py
│   │   └── funcao.py
│   └── models/           # Modelos de dados
├── tests/                # Testes automatizados
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Como Rodar os Testes

```bash
pytest tests/ -v
```

## Endpoints Principais

Todos os endpoints protegidos exigem um token Firebase (Bearer Token) no header `Authorization`.

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

Parametros de query opcionais para `/relatorios`: `profissional_id`, `data_inicio` (DD/MM/AAAA), `data_fim` (DD/MM/AAAA), `local`, `status`.

## Deploy

- **Plataforma:** Render
- **CI/CD:** GitHub Actions com pipeline automatico no push para `main`
  - Job `test` — roda os testes com pytest
  - Job `deploy` — aciona o deploy no Render via Deploy Hook
