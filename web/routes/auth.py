"""인증 라우트."""

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from web.dependencies import get_app_settings
from web.settings import Settings

router = APIRouter(tags=["auth"])


@router.get("/login")
def login_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "login.html",
        {"auth_disabled": request.app.state.settings.auth_disabled},
    )


@router.post("/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    settings: Settings = Depends(get_app_settings),
):
    if settings.auth_disabled:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            "access_token",
            "dev-token",
            httponly=True,
            samesite="lax",
            secure=settings.cookie_secure,
        )
        return response

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.supabase_url}/auth/v1/token?grant_type=password",
            json={"email": email, "password": password},
            headers={
                "apikey": settings.supabase_anon_key,
                "Content-Type": "application/json",
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="로그인 응답이 올바르지 않습니다.")

    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return redirect


@router.post("/auth/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
