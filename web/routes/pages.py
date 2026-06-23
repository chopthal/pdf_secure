"""HTML 페이지."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from web.auth import AuthUser, get_current_user
from web.dependencies import get_app_settings, get_job_service
from web.services.job_service import JobService
from web.settings import Settings

router = APIRouter(tags=["pages"])


def _optional_user(request: Request, settings: Settings) -> AuthUser | None:
    try:
        return get_current_user(request, settings)
    except HTTPException:
        return None


@router.get("/")
def index(
    request: Request,
    settings: Settings = Depends(get_app_settings),
):
    user = _optional_user(request, settings)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "user": user,
            "default_watermark_start_page": settings.default_watermark_start_page,
        },
    )


@router.get("/jobs/{job_id}")
def job_progress_page(
    job_id: str,
    request: Request,
    settings: Settings = Depends(get_app_settings),
    job_service: JobService = Depends(get_job_service),
):
    user = _optional_user(request, settings)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "job.html",
        {"job_id": job_id, "user": user},
    )
