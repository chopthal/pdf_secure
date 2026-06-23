"""REST API — 작업."""

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from web.auth import AuthUser
from web.dependencies import get_app_settings, get_job_service, require_user
from web.services.job_service import JobService, JobValidationError
from web.settings import Settings

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("")
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    buyer_name: str = Form(...),
    buyer_phone: str = Form(...),
    pdf_password: str = Form(...),
    watermark_start_page: int = Form(5),
    user: AuthUser = Depends(require_user),
    job_service: JobService = Depends(get_job_service),
    settings: Settings = Depends(get_app_settings),
):
    content = await file.read()
    try:
        job = job_service.create_job(
            file_content=content,
            original_filename=file.filename or "document.pdf",
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            pdf_password=pdf_password,
            watermark_start_page=watermark_start_page,
            user_id=user.user_id,
        )
    except JobValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(
        job_service.process_job,
        job.job_id,
        pdf_password,
        watermark_start_page,
    )
    return {"job_id": job.job_id, **job.to_api_dict()}


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    user: AuthUser = Depends(require_user),
    job_service: JobService = Depends(get_job_service),
):
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    return job.to_api_dict()


@router.get("/{job_id}/download")
def download_job(
    job_id: str,
    user: AuthUser = Depends(require_user),
    job_service: JobService = Depends(get_job_service),
):
    from web.models.job import JobStatus

    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    if job.status != JobStatus.DONE or job.output_path is None:
        raise HTTPException(status_code=409, detail="아직 다운로드할 수 없습니다.")
    if not job.output_path.is_file():
        raise HTTPException(status_code=404, detail="결과 파일이 없습니다.")
    return FileResponse(
        path=job.output_path,
        filename=job.output_filename or "output.pdf",
        media_type="application/pdf",
    )


@router.delete("/{job_id}")
def delete_job(
    job_id: str,
    user: AuthUser = Depends(require_user),
    job_service: JobService = Depends(get_job_service),
):
    if not job_service.delete_job(job_id):
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    return {"deleted": True}
