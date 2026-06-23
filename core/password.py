"""PDF 비밀번호 검증.

PDF 암호화는 뷰어·인코딩마다 한글 등 비ASCII 문자 처리가 달라
나중에 열리지 않는 경우가 있어, 호환 가능한 문자만 허용한다.
"""

import re

# PDF 1.7 / pypdf 호환: 인쇄 가능 ASCII (공백 U+0020 ~ 물결 U+007E)
PDF_PASSWORD_PATTERN = re.compile(r"^[ -~]+$")
PDF_PASSWORD_MAX_LENGTH = 128

PDF_PASSWORD_RULE_MESSAGE = (
    "PDF 비밀번호는 영문, 숫자, 기본 특수문자만 사용할 수 있습니다. (한글 불가)"
)


class PdfPasswordValidationError(ValueError):
    """PDF 비밀번호 형식 오류."""


def is_valid_pdf_password(password: str) -> bool:
    if not password or len(password) > PDF_PASSWORD_MAX_LENGTH:
        return False
    return PDF_PASSWORD_PATTERN.fullmatch(password) is not None


def validate_pdf_password(password: str) -> None:
    if not password.strip():
        raise PdfPasswordValidationError("PDF 비밀번호를 입력해주세요.")
    if len(password) > PDF_PASSWORD_MAX_LENGTH:
        raise PdfPasswordValidationError(
            f"PDF 비밀번호는 {PDF_PASSWORD_MAX_LENGTH}자 이하여야 합니다."
        )
    if not PDF_PASSWORD_PATTERN.fullmatch(password):
        raise PdfPasswordValidationError(PDF_PASSWORD_RULE_MESSAGE)
