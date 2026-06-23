"""Task: core/password 단위 테스트."""

import pytest

from core.password import (
    PDF_PASSWORD_MAX_LENGTH,
    PDF_PASSWORD_RULE_MESSAGE,
    is_valid_pdf_password,
    validate_pdf_password,
)


class TestPdfPassword:
    def test_accepts_ascii_alphanumeric(self):
        validate_pdf_password("pass123")
        assert is_valid_pdf_password("Abc_123-!")

    def test_rejects_korean(self):
        with pytest.raises(ValueError, match="한글"):
            validate_pdf_password("비밀번호")
        assert not is_valid_pdf_password("abc한글")

    def test_rejects_emoji(self):
        assert not is_valid_pdf_password("pass🔒")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="입력"):
            validate_pdf_password("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match=str(PDF_PASSWORD_MAX_LENGTH)):
            validate_pdf_password("a" * (PDF_PASSWORD_MAX_LENGTH + 1))

    def test_rule_message_constant(self):
        assert "한글" in PDF_PASSWORD_RULE_MESSAGE
