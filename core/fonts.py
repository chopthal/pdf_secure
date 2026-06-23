"""한글 워터마크 폰트 해석·등록."""

import os
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.config import (
    BUNDLED_FONTS_DIR,
    DEFAULT_BUNDLED_FONT_FILENAME,
    DEFAULT_BUNDLED_FONT_NAME,
    PROJECT_ROOT,
)

FALLBACK_FONT_NAME = "Helvetica"


def resolve_bundled_font_path(fonts_dir: Path | None = None) -> Path | None:
    """
    번들 폰트 파일 경로를 반환. 없으면 None.

    우선순위:
    1. 환경 변수 PDF_SECURE_FONT_PATH
    2. assets/fonts/NanumGothic.ttf
    """
    env_path = os.environ.get("PDF_SECURE_FONT_PATH")
    if env_path:
        path = Path(env_path)
        if path.is_file():
            return path

    base = fonts_dir if fonts_dir is not None else BUNDLED_FONTS_DIR
    bundled = base / DEFAULT_BUNDLED_FONT_FILENAME
    if bundled.is_file():
        return bundled

    return None


def register_watermark_font(
    font_path: Path | None = None,
    font_register_name: str = DEFAULT_BUNDLED_FONT_NAME,
) -> str:
    """
    워터마크용 TTF 폰트를 reportlab에 등록하고 사용할 폰트 이름을 반환.

    font_path가 없으면 번들·환경 변수 경로를 탐색한다.
    실패 시 Helvetica(한글 깨짐 가능).
    """
    path = font_path or resolve_bundled_font_path()
    if path is None:
        return FALLBACK_FONT_NAME

    try:
        pdfmetrics.registerFont(TTFont(font_register_name, str(path)))
        return font_register_name
    except Exception:
        return FALLBACK_FONT_NAME


def get_korean_font() -> str:
    """워터마크용 한글 폰트 이름 (웹·서버 환경용 — 번들 폰트 우선)."""
    return register_watermark_font()
