"""Supabase JWT 인증."""

from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status

from web.settings import Settings


@dataclass
class AuthUser:
    user_id: str
    email: str | None = None


def decode_supabase_jwt(token: str, jwt_secret: str) -> AuthUser:
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다.",
        )
    return AuthUser(user_id=user_id, email=payload.get("email"))


def extract_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip() or None
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    return None


def get_current_user(request: Request, settings: Settings) -> AuthUser:
    if settings.auth_disabled:
        return AuthUser(user_id="dev-user", email="dev@local.test")

    token = extract_bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )
    return decode_supabase_jwt(token, settings.supabase_jwt_secret)


def create_access_token(
    user_id: str,
    email: str,
    jwt_secret: str,
    *,
    expires_minutes: int = 60,
) -> str:
    """테스트·개발용 JWT 생성."""
    import time

    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "iat": now,
        "exp": now + expires_minutes * 60,
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")
