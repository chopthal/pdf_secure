"""워터마크·경로 등 공통 설정."""

from pathlib import Path

# 프로젝트 루트 (core/ 의 상위)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

BUNDLED_FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"
DEFAULT_BUNDLED_FONT_FILENAME = "NanumGothic.ttf"
DEFAULT_BUNDLED_FONT_NAME = "NanumGothic"

# 워터마크 기본값 (DEVELOPMENT.md / web_migration_dev.md 스펙)
DEFAULT_WATERMARK_START_PAGE = 5  # 1-based (UI 표시용)
DEFAULT_WATERMARK_FONT_SIZE = 10
DEFAULT_WATERMARK_X = 30
DEFAULT_WATERMARK_Y_OFFSET = 30  # y = Y_OFFSET + font_size * 1.5
DEFAULT_WATERMARK_GRAY = 0.5
DEFAULT_WATERMARK_ALPHA = 0.6

METADATA_AUTHOR = "올라"
METADATA_CREATOR = "올라의 꿀수면 프로젝트"


def page_number_to_index(page_number: int) -> int:
    """
    UI 1-based 페이지 번호를 0-based 인덱스로 변환.

    예: 5페이지 → 인덱스 4
    """
    if page_number < 1:
        raise ValueError(f"페이지 번호는 1 이상이어야 합니다: {page_number}")
    return page_number - 1


def watermark_page_indices(total_pages: int, start_page_index: int) -> list[int]:
    """워터마크를 적용할 페이지 인덱스 목록."""
    if total_pages < 0:
        raise ValueError(f"total_pages는 0 이상이어야 합니다: {total_pages}")
    if start_page_index < 0:
        raise ValueError(f"start_page_index는 0 이상이어야 합니다: {start_page_index}")
    return [i for i in range(total_pages) if i >= start_page_index]
