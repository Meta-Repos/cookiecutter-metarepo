"""
PyTest configuration and fixtures.
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio

@pytest.fixture
def test_config() -> Dict:
    """Provide test configuration."""
    return {
        "core": {
            "log_level": "debug",
            "event_log_path": "logs/events.log"
        },
        "events": {
            "host": "127.0.0.1",
            "port": 5556,  # Different port for testing
            "protocol": "tcp"
        },
        "plugins": {
            "enabled": [],
            "search_paths": ["plugins"]
        }
    }

@pytest.fixture
def temp_log_path(tmp_path: Path) -> Path:
    """Provide a temporary log path."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir / "events.log"

@pytest_asyncio.fixture
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()