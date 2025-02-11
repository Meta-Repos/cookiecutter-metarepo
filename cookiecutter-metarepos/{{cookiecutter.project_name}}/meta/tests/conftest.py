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

@pytest.fixture(autouse=True)
def _setup_test_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Set up test environment variables and paths."""
    # Set up temporary directories
    monkeypatch.setenv("METAREPOS_HOME", str(tmp_path))
    monkeypatch.setenv("METAREPOS_CONFIG", str(tmp_path / "config"))
    monkeypatch.setenv("METAREPOS_LOGS", str(tmp_path / "logs"))
    monkeypatch.setenv("METAREPOS_PLUGINS", str(tmp_path / "plugins"))
    
    # Create necessary directories
    (tmp_path / "config").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "plugins").mkdir()

@pytest.fixture
def plugin_test_config() -> Dict:
    """Provide test configuration for plugins."""
    return {
        "name": "test-plugin",
        "version": "0.1.0",
        "author": "Test Author",
        "description": "A test plugin",
        "config": {
            "log_level": "debug",
            "retry_count": 3,
            "enabled_features": ["feature1", "feature2"],
            "advanced": {
                "timeout": 30.0,
                "max_size": 1048576
            }
        }
    }

@pytest.fixture
def freezer(monkeypatch: pytest.MonkeyPatch):
    """Provide a simple time freezing fixture."""
    from datetime import datetime
    
    class TimeFreeze:
        def __init__(self):
            self.current_time = datetime.utcnow()
        
        def move_to(self, date_str: str):
            """Move time to a specific date."""
            self.current_time = datetime.fromisoformat(date_str)
            monkeypatch.setattr(
                "datetime.datetime.utcnow",
                lambda: self.current_time
            )
    
    return TimeFreeze()