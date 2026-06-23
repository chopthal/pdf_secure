"""대용량 PDF 처리 (Phase 3 E2E)."""

from pathlib import Path

import pytest
from pypdf import PdfReader

from core.watermark import add_watermark
from tests.conftest import _write_multipage_pdf


@pytest.mark.slow
def test_process_200_page_pdf(tmp_path):
    """200페이지 PDF 워터마크 처리 (로컬·CI 선택 실행: pytest -m slow)."""
    input_path = tmp_path / "large_200.pdf"
    output_path = tmp_path / "large_200_out.pdf"
    _write_multipage_pdf(input_path, page_count=200)

    add_watermark(
        input_path,
        output_path,
        "이 책은 테스트 (010) 님이 구매하신 전자책입니다.",
        password="test1234",
        buyer_name="테스트",
        buyer_phone="010",
        watermark_start_page=5,
    )

    reader = PdfReader(str(output_path))
    reader.decrypt("test1234")
    assert len(reader.pages) == 200
    assert output_path.stat().st_size > 0


def test_process_20_page_pdf_smoke(tmp_path):
    """배포 전 기본 대용량 스모크 (일반 pytest 포함)."""
    input_path = tmp_path / "medium_20.pdf"
    output_path = tmp_path / "medium_20_out.pdf"
    _write_multipage_pdf(input_path, page_count=20)

    add_watermark(
        input_path,
        output_path,
        "이 책은 테스트 (010) 님이 구매하신 전자책입니다.",
        watermark_start_page=5,
    )

    assert len(PdfReader(str(output_path)).pages) == 20
