from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.routers import audit, auth, documents, sensible, standard, utilisateurs
from app.core.config import settings


from app.db.session import init_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation de l'administrateur initial au démarrage
    await init_admin()
    yield


app = FastAPI(
    title="CSI Sakaraha Backend",
    version="1.0.0",
    description="API de gestion des registres CSI Sakaraha.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Contrainte de donnees violee"})


@app.get("/health", tags=["systeme"])
async def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(utilisateurs.router, prefix="/api/v1")
app.include_router(standard.router, prefix="/api/v1")
app.include_router(sensible.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
