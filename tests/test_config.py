"""Task 1: core/config 단위 테스트."""

import pytest

from core.config import (
    DEFAULT_WATERMARK_START_PAGE,
    page_number_to_index,
    watermark_page_indices,
)


class TestPageNumberToIndex:
    def test_default_start_page_maps_to_index_four(self):
        assert page_number_to_index(DEFAULT_WATERMARK_START_PAGE) == 4

    def test_first_page_maps_to_zero(self):
        assert page_number_to_index(1) == 0

    def test_rejects_zero(self):
        with pytest.raises(ValueError, match="1 이상"):
            page_number_to_index(0)

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="1 이상"):
            page_number_to_index(-1)


class TestWatermarkPageIndices:
    def test_default_six_pages_watermarks_last_two(self):
        # 6페이지 PDF, 5페이지(인덱스 4)부터 → 인덱스 4, 5
        indices = watermark_page_indices(6, page_number_to_index(5))
        assert indices == [4, 5]

    def test_start_from_first_page_watermarks_all(self):
        indices = watermark_page_indices(3, page_number_to_index(1))
        assert indices == [0, 1, 2]

    def test_start_beyond_page_count_returns_empty(self):
        indices = watermark_page_indices(4, page_number_to_index(10))
        assert indices == []

    def test_zero_pages_returns_empty(self):
        assert watermark_page_indices(0, 0) == []

    def test_rejects_negative_total_pages(self):
        with pytest.raises(ValueError, match="total_pages"):
            watermark_page_indices(-1, 0)

    def test_rejects_negative_start_index(self):
        with pytest.raises(ValueError, match="start_page_index"):
            watermark_page_indices(5, -1)
