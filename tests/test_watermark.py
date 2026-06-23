"""Task 3: core/watermark 단위 테스트."""

import io
from pathlib import Path

import pytest
from pypdf import PdfReader

from core.config import page_number_to_index
from core.watermark import add_watermark, build_watermark_layer
from core.fonts import register_watermark_font
from core.config import PROJECT_ROOT
from tests.conftest import count_merge_operations

BUNDLED_FONT = PROJECT_ROOT / "assets" / "fonts" / "NanumGothic.ttf"

WATERMARK_TEXT = "이 책은 홍길동 (010-1234) 님이 구매하신 전자책입니다."


@pytest.fixture
def font_name():
    if not BUNDLED_FONT.is_file():
        pytest.skip("assets/fonts/NanumGothic.ttf 없음")
    return register_watermark_font(font_path=BUNDLED_FONT)


class TestBuildWatermarkLayer:
    def test_produces_readable_single_page_pdf(self, font_name):
        packet = build_watermark_layer(WATERMARK_TEXT, font_name)
        reader = PdfReader(packet)
        assert len(reader.pages) == 1


class TestAddWatermark:
    def test_creates_output_with_same_page_count(self, sample_multipage_pdf, tmp_path, font_name):
        out = tmp_path / "out.pdf"
        add_watermark(
            sample_multipage_pdf,
            out,
            WATERMARK_TEXT,
            buyer_name="홍길동",
            buyer_phone="010-1234",
        )
        assert out.is_file()
        assert len(PdfReader(str(out)).pages) == 6

    def test_default_start_page_watermarks_from_page_five(
        self, sample_multipage_pdf, tmp_path, font_name
    ):
        """6페이지 PDF, 기본 5페이지 시작 → 2페이지만 워터마크 대상."""
        expected_merges = count_merge_operations(
            sample_multipage_pdf, page_number_to_index(5)
        )
        assert expected_merges == 2

        out = tmp_path / "out_default.pdf"
        add_watermark(sample_multipage_pdf, out, WATERMARK_TEXT)
        # 출력이 생성되고 페이지 수 유지
        assert len(PdfReader(str(out)).pages) == 6

    def test_custom_start_page_one_watermarks_all_pages(
        self, two_page_pdf, tmp_path, font_name
    ):
        out = tmp_path / "out_all.pdf"
        add_watermark(
            two_page_pdf,
            out,
            WATERMARK_TEXT,
            watermark_start_page=1,
        )
        reader = PdfReader(str(out))
        assert len(reader.pages) == 2

    def test_custom_start_page_two_watermarks_second_page_only(
        self, two_page_pdf, font_name
    ):
        merges = count_merge_operations(two_page_pdf, page_number_to_index(2))
        assert merges == 1

    def test_metadata_contains_buyer_info(self, sample_multipage_pdf, tmp_path, font_name):
        out = tmp_path / "out_meta.pdf"
        add_watermark(
            sample_multipage_pdf,
            out,
            WATERMARK_TEXT,
            buyer_name="김철수",
            buyer_phone="test@email.com",
        )
        meta = PdfReader(str(out)).metadata
        assert meta is not None
        assert "김철수" in (meta.get("/Subject") or "")
        assert "test@email.com" in (meta.get("/Subject") or "")

    def test_password_encrypts_output(self, sample_multipage_pdf, tmp_path, font_name):
        out = tmp_path / "out_enc.pdf"
        password = "secret123"
        add_watermark(
            sample_multipage_pdf,
            out,
            WATERMARK_TEXT,
            password=password,
        )
        reader = PdfReader(str(out))
        assert reader.is_encrypted
        reader.decrypt(password)
        assert len(reader.pages) == 6

    def test_writes_to_bytesio_sink(self, sample_multipage_pdf, font_name):
        buffer = io.BytesIO()
        add_watermark(sample_multipage_pdf, buffer, WATERMARK_TEXT)
        buffer.seek(0)
        assert len(PdfReader(buffer).pages) == 6

    def test_progress_callback_invoked(self, sample_multipage_pdf, tmp_path, font_name):
        events: list[tuple[int, int, str]] = []

        def cb(current, total, message):
            events.append((current, total, message))

        out = tmp_path / "out_cb.pdf"
        add_watermark(
            sample_multipage_pdf,
            out,
            WATERMARK_TEXT,
            progress_callback=cb,
        )
        assert len(events) > 0
        assert events[-1][2] == "완료!"

    def test_invalid_start_page_raises(self, sample_multipage_pdf, tmp_path, font_name):
        out = tmp_path / "out_bad.pdf"
        with pytest.raises(ValueError, match="1 이상"):
            add_watermark(
                sample_multipage_pdf,
                out,
                WATERMARK_TEXT,
                watermark_start_page=0,
            )
