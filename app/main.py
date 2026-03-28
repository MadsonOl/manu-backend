import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from app.routers import chamados, ordens_servico, profissionais, empresas, funcoes, relatorios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manu")

app = FastAPI(
    title="Manu API",
    description="API do sistema de gestao de manutencoes Manu",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/", tags=["Root"])
async def root():
    return {"status": "online", "message": "Manu API funcionando"}
