"""FastAPI 애플리케이션."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.routes import auth, jobs, pages
from web.services.cleanup import cleanup_expired_jobs
from web.services.job_service import JobService
from web.services.job_store import JobStore
from core.config import PROJECT_ROOT
from web.settings import Settings

WEB_ROOT = PROJECT_ROOT / "web"
TEMPLATES_DIR = WEB_ROOT / "templates"
STATIC_DIR = WEB_ROOT / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    settings.validate_auth_config()
    yield
    cleanup_expired_jobs(app.state.job_store)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings.from_env()
    store = JobStore()
    job_service = JobService(store, resolved)

    app = FastAPI(title="PDF 보안 처리", lifespan=lifespan)
    app.state.settings = resolved
    app.state.job_store = store
    app.state.job_service = job_service
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(jobs.router)
    return app


app = create_app()
