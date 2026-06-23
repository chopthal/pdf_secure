"""FastAPI 의존성."""

from fastapi import Depends, Request

from web.auth import AuthUser, get_current_user
from web.services.job_service import JobService
from web.services.job_store import JobStore
from web.settings import Settings


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_job_store(request: Request) -> JobStore:
    return request.app.state.job_store


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service


def require_user(
    request: Request,
    settings: Settings = Depends(get_app_settings),
) -> AuthUser:
    return get_current_user(request, settings)
