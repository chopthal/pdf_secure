"""공통 pytest 픽스처."""

import io
from pathlib import Path

import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


@pytest.fixture
def sample_multipage_pdf(tmp_path) -> Path:
    """6페이지 테스트용 PDF."""
    path = tmp_path / "sample_6pages.pdf"
    _write_multipage_pdf(path, page_count=6)
    return path


@pytest.fixture
def two_page_pdf(tmp_path) -> Path:
    path = tmp_path / "sample_2pages.pdf"
    _write_multipage_pdf(path, page_count=2)
    return path


def _write_multipage_pdf(path: Path, page_count: int) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    for i in range(page_count):
        c.drawString(100, 700, f"Page {i + 1}")
        c.showPage()
    c.save()


def count_merge_operations(input_path: Path, start_page_index: int) -> int:
    """워터마크 병합 횟수를 시뮬레이션 (config 로직과 동일)."""
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    return sum(1 for i in range(total) if i >= start_page_index)
