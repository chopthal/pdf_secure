FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PDF_SECURE_TEMP_ROOT=/tmp/pdf_secure

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY core/ core/
COPY web/ web/
COPY assets/fonts/ assets/fonts/

EXPOSE 8000

CMD ["sh", "-c", "uvicorn web.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
