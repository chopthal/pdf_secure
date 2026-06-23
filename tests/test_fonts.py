"""Task 2: core/fonts 단위 테스트."""

from pathlib import Path

import pytest
from reportlab.pdfbase import pdfmetrics

from core.config import DEFAULT_BUNDLED_FONT_NAME, PROJECT_ROOT
from core.fonts import (
    FALLBACK_FONT_NAME,
    register_watermark_font,
    resolve_bundled_font_path,
)

BUNDLED_FONT = PROJECT_ROOT / "assets" / "fonts" / "NanumGothic.ttf"


@pytest.fixture
def fonts_dir(tmp_path):
    """테스트용 폰트 디렉터리."""
    return tmp_path / "fonts"


class TestResolveBundledFontPath:
    def test_finds_project_bundled_nanum_gothic(self):
        if not BUNDLED_FONT.is_file():
            pytest.skip("assets/fonts/NanumGothic.ttf 없음 — 폰트 파일을 추가하세요")
        path = resolve_bundled_font_path()
        assert path is not None
        assert path.name == "NanumGothic.ttf"

    def test_env_override(self, fonts_dir, monkeypatch):
        if not BUNDLED_FONT.is_file():
            pytest.skip("번들 폰트 없음")
        fonts_dir.mkdir(parents=True, exist_ok=True)
        custom = fonts_dir / "custom.ttf"
        custom.write_bytes(BUNDLED_FONT.read_bytes())
        monkeypatch.setenv("PDF_SECURE_FONT_PATH", str(custom))
        assert resolve_bundled_font_path() == custom

    def test_missing_font_returns_none(self, fonts_dir):
        assert resolve_bundled_font_path(fonts_dir=fonts_dir) is None


class TestRegisterWatermarkFont:
    def test_registers_bundled_font(self):
        if not BUNDLED_FONT.is_file():
            pytest.skip("assets/fonts/NanumGothic.ttf 없음")
        unique_name = "NanumGothicTestRegister"
        name = register_watermark_font(
            font_path=BUNDLED_FONT,
            font_register_name=unique_name,
        )
        assert name == unique_name
        assert unique_name in pdfmetrics.getRegisteredFontNames()

    def test_missing_file_returns_helvetica(self, fonts_dir):
        missing = fonts_dir / "nope.ttf"
        assert register_watermark_font(font_path=missing) == FALLBACK_FONT_NAME

    def test_get_korean_font_uses_bundled_when_present(self):
        if not BUNDLED_FONT.is_file():
            pytest.skip("assets/fonts/NanumGothic.ttf 없음")
        from core.fonts import get_korean_font

        assert get_korean_font() == DEFAULT_BUNDLED_FONT_NAME
