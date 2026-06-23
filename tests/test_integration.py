"""pdf_secure.py가 core를 올바르게 re-export하는지 검증."""

import importlib
from pathlib import Path

import pytest
from pypdf import PdfReader

from core.config import PROJECT_ROOT
from tests.conftest import _write_multipage_pdf

BUNDLED_FONT = PROJECT_ROOT / "assets" / "fonts" / "NanumGothic.ttf"

tkinter = pytest.importorskip("tkinter", reason="tkinter 미설치 환경(GUI 미사용)")


@pytest.fixture
def six_page_pdf(tmp_path) -> Path:
    path = tmp_path / "six.pdf"
    _write_multipage_pdf(path, 6)
    return path


class TestPdfSecureReexport:
    def test_add_watermark_via_legacy_entrypoint(self, six_page_pdf, tmp_path):
        if not BUNDLED_FONT.is_file():
            pytest.skip("assets/fonts/NanumGothic.ttf 없음")
        pdf_secure = importlib.import_module("pdf_secure")
        out = tmp_path / "legacy_out.pdf"
        result = pdf_secure.add_watermark(
            str(six_page_pdf),
            str(out),
            "이 책은 테스트 (010) 님이 구매하신 전자책입니다.",
            buyer_name="테스트",
            buyer_phone="010",
        )
        assert result is True
        assert len(PdfReader(str(out)).pages) == 6
