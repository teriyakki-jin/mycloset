"""인증 엔드포인트 통합 테스트."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def anon_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestRegister:
    async def test_register_success(self, anon_client):
        from datetime import datetime, timezone
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        def fake_add(obj):
            obj.created_at = datetime.now(timezone.utc)

        mock_session.add = fake_add
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()

        from src.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_session

        with patch("src.utils.security.hash_password", return_value="hashed"):
            resp = await anon_client.post("/auth/register", json={
                "email": "new@example.com",
                "password": "password123",
                "display_name": "새 유저",
            })

        app.dependency_overrides.clear()
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"

    async def test_register_duplicate_email(self, anon_client):
        existing_user = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        from src.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_session

        resp = await anon_client.post("/auth/register", json={
            "email": "exist@example.com",
            "password": "password123",
            "display_name": "중복 유저",
        })

        app.dependency_overrides.clear()
        assert resp.status_code == 409

    async def test_register_invalid_email(self, anon_client):
        resp = await anon_client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
            "display_name": "유저",
        })
        assert resp.status_code == 422


class TestLogin:
    async def test_login_wrong_password(self, anon_client):
        from src.models.user import User
        mock_user = MagicMock(spec=User)
        mock_user.hashed_password = "hashed"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        from src.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_session

        with patch("src.routers.auth.verify_password", return_value=False):
            resp = await anon_client.post("/auth/login", json={
                "email": "user@example.com",
                "password": "wrongpassword",
            })

        app.dependency_overrides.clear()
        assert resp.status_code == 401

    async def test_login_user_not_found(self, anon_client):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        from src.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_session

        resp = await anon_client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })

        app.dependency_overrides.clear()
        assert resp.status_code == 401
