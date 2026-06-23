"""Task 1: 배포 파일 검증."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestDeployFiles:
    def test_dockerfile_exists_and_uses_uvicorn(self):
        dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "python:3.12-slim" in dockerfile
        assert "uvicorn web.main:app" in dockerfile
        assert "requirements-prod.txt" in dockerfile

    def test_railway_toml_healthcheck(self):
        content = (PROJECT_ROOT / "railway.toml").read_text(encoding="utf-8")
        assert "/health" in content

    def test_requirements_prod_excludes_pyinstaller(self):
        content = (PROJECT_ROOT / "requirements-prod.txt").read_text(encoding="utf-8")
        assert "fastapi" in content
        assert "pyinstaller" not in content.lower()

    def test_dockerignore_excludes_tests(self):
        content = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")
        assert "tests/" in content
