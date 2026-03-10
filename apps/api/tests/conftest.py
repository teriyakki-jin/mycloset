"""공통 테스트 픽스처."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.dependencies import get_current_user, get_db
from src.main import app
from src.models.user import User


# ── 테스트용 유저 ─────────────────────────────────────────
@pytest.fixture
def test_user() -> User:
    user = MagicMock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "test@example.com"
    user.display_name = "테스트유저"
    user.created_at = datetime.now(timezone.utc)
    return user


# ── DB mock ────────────────────────────────────────────────
@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


# ── 인증된 클라이언트 (dependency override) ───────────────
@pytest.fixture
async def client(test_user, mock_db):
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ── 비인증 클라이언트 ─────────────────────────────────────
@pytest.fixture
async def anon_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
