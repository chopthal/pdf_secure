"""PDF 워터마크·메타데이터·암호화."""

import io
from pathlib import Path
from typing import BinaryIO, Callable, Union

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

from core.config import (
    DEFAULT_WATERMARK_ALPHA,
    DEFAULT_WATERMARK_FONT_SIZE,
    DEFAULT_WATERMARK_GRAY,
    DEFAULT_WATERMARK_START_PAGE,
    DEFAULT_WATERMARK_X,
    DEFAULT_WATERMARK_Y_OFFSET,
    METADATA_AUTHOR,
    METADATA_CREATOR,
    page_number_to_index,
    watermark_page_indices,
)
from core.fonts import register_watermark_font

PathLike = Union[str, Path]
PdfSource = Union[PathLike, BinaryIO]
PdfSink = Union[PathLike, BinaryIO]

ProgressCallback = Callable[[int, int, str], None]


def build_watermark_layer(
    watermark_text: str,
    font_name: str,
    font_size: int = DEFAULT_WATERMARK_FONT_SIZE,
) -> io.BytesIO:
    """워터마크 단일 페이지 PDF를 메모리에 생성."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont(font_name, font_size)
    can.setFillColorRGB(DEFAULT_WATERMARK_GRAY, DEFAULT_WATERMARK_GRAY, DEFAULT_WATERMARK_GRAY)
    can.setFillAlpha(DEFAULT_WATERMARK_ALPHA)
    can.drawString(
        DEFAULT_WATERMARK_X,
        DEFAULT_WATERMARK_Y_OFFSET + font_size * 1.5,
        watermark_text,
    )
    can.save()
    packet.seek(0)
    return packet


def _open_reader(source: PdfSource) -> PdfReader:
    if isinstance(source, (str, Path)):
        return PdfReader(str(source))
    return PdfReader(source)


def _write_output(writer: PdfWriter, sink: PdfSink) -> None:
    if isinstance(sink, (str, Path)):
        with open(sink, "wb") as stream:
            writer.write(stream)
    else:
        writer.write(sink)
        if hasattr(sink, "seek"):
            sink.seek(0)


def add_watermark(
    input_pdf: PdfSource,
    output_pdf: PdfSink,
    watermark_text: str,
    password: str | None = None,
    buyer_name: str | None = None,
    buyer_phone: str | None = None,
    watermark_start_page: int = DEFAULT_WATERMARK_START_PAGE,
    progress_callback: ProgressCallback | None = None,
) -> bool:
    """
    PDF에 워터마크·메타데이터·비밀번호를 적용한다.

    watermark_start_page: 1-based 시작 페이지 (기본 5 = 5번째 페이지부터)
    """
    start_page_index = page_number_to_index(watermark_start_page)
    font_name = register_watermark_font()

    watermark_packet = build_watermark_layer(watermark_text, font_name)
    watermark_page = PdfReader(watermark_packet).pages[0]

    existing_pdf = _open_reader(input_pdf)
    output = PdfWriter()

    total_pages = len(existing_pdf.pages)
    if progress_callback:
        progress_callback(0, total_pages, "PDF 읽기 완료")

    indices_to_watermark = set(
        watermark_page_indices(total_pages, start_page_index)
    )

    for i in range(total_pages):
        page = existing_pdf.pages[i]
        if i in indices_to_watermark:
            page.merge_page(watermark_page)
        output.add_page(page)

        if progress_callback:
            progress_callback(
                i + 1, total_pages, f"페이지 처리 중: {i + 1}/{total_pages}"
            )

    if buyer_name or buyer_phone:
        if progress_callback:
            progress_callback(total_pages, total_pages, "메타데이터 설정 중...")

        metadata = {}
        if hasattr(existing_pdf, "metadata") and existing_pdf.metadata:
            metadata = existing_pdf.metadata.copy()

        metadata.update(
            {
                "/Author": METADATA_AUTHOR,
                "/Subject": f"구매자 정보: {buyer_name or ''} ({buyer_phone or ''})",
                "/Creator": METADATA_CREATOR,
                "/Producer": "",
            }
        )
        output.add_metadata(metadata)

    if password:
        if progress_callback:
            progress_callback(
                total_pages, total_pages, "비밀번호 및 권한 설정 중..."
            )
        output.encrypt(
            user_password=password,
            owner_password=password,
            use_128bit=True,
        )

    if progress_callback:
        progress_callback(total_pages, total_pages, "파일 저장 중...")

    _write_output(output, output_pdf)

    if progress_callback:
        progress_callback(total_pages, total_pages, "완료!")

    return True
