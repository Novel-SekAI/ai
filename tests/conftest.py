from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sekai_ai.app import create_app
from sekai_ai.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env="test", _env_file=None)


@pytest_asyncio.fixture
async def client(settings: Settings) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=create_app(settings))
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
