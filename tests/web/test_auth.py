"""Task 3: web/auth 단위 테스트."""

import pytest
from fastapi import HTTPException

from web.auth import AuthUser, create_access_token, decode_supabase_jwt


class TestSupabaseJwt:
    def test_roundtrip_token(self):
        secret = "test-secret-key-for-jwt-signing-32b"
        token = create_access_token("user-abc", "test@example.com", secret)
        user = decode_supabase_jwt(token, secret)
        assert user == AuthUser(user_id="user-abc", email="test@example.com")

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_supabase_jwt("not.valid.token", "secret")
        assert exc.value.status_code == 401
