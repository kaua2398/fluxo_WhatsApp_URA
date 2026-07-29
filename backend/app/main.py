from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.flows import router as flow_detail_router
from app.api.routes.projects import flows_router, router as projects_router, upload_router
from app.core.config import get_settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_directories()
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API para navegação e documentação visual de fluxos de atendimento",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.api_prefix
    app.include_router(projects_router, prefix=prefix)
    app.include_router(flows_router, prefix=prefix)
    app.include_router(upload_router, prefix=prefix)
    app.include_router(flow_detail_router, prefix=prefix)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": settings.app_version}

    @app.get("/")
    async def root():
        return JSONResponse(
            {
                "name": settings.app_name,
                "version": settings.app_version,
                "docs": "/docs",
                "api": settings.api_prefix,
            }
        )

    return app


app = create_app()
