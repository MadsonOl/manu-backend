import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from app.routers import chamados, ordens_servico, profissionais, empresas, funcoes, relatorios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manu")

app = FastAPI(
    title="manu API",
    description="""
API do sistema manu — plataforma de gestao de manutencoes.

## Autenticacao
A maioria dos endpoints exige um token Firebase JWT no header:
`Authorization: Bearer <token>`

## Endpoints publicos (sem autenticacao)
- `POST /chamados` — abertura de chamado por usuario externo
- `GET /` — status da API

## Fluxo principal
1. Gestor se autentica via Firebase Auth
2. Chamado e aberto por usuario externo via link publico
3. Gestor converte chamado em ordem de servico
4. Ordem e atribuida a um profissional cadastrado
5. Gestor finaliza a ordem quando concluida
6. Relatorios filtrados ficam disponiveis para impressao
    """,
    version="1.0.0",
    contact={
        "name": "Suporte manu",
        "email": "suporte@manu.app"
    },
    license_info={
        "name": "MIT"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
        "http://127.0.0.1:5180",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Erro de validacao 422: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno em {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


app.include_router(chamados.router)
app.include_router(ordens_servico.router)
app.include_router(profissionais.router)
app.include_router(empresas.router)
app.include_router(funcoes.router)
app.include_router(relatorios.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido via Firebase Authentication"
        }
    }
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", tags=["Root"])
async def root():
    return {"status": "online", "message": "Manu API funcionando"}
