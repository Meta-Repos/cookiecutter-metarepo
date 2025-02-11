"""
Tests for {{ cookiecutter.plugin_name }}.
"""
import asyncio
from pathlib import Path
from typing import Dict

import pytest
import pytest_asyncio
from metarepos.core.events import Event, EventManager

from ..plugin import Plugin

@pytest.fixture
def plugin_metadata() -> Dict:
    """Provide plugin metadata for testing."""
    return {
        "name": "{{ cookiecutter.plugin_name }}",
        "version": "{{ cookiecutter.version }}",
        "author": "{{ cookiecutter.author_name }}",
        "description": "{{ cookiecutter.plugin_description }}",
        "config": {
            # Add test configuration here
        }
    }

@pytest_asyncio.fixture
async def event_manager(tmp_path: Path) -> EventManager:
    """Provide a configured event manager."""
    config = {
        "events": {
            "host": "127.0.0.1",
            "port": 5557,
            "protocol": "tcp"
        }
    }
    manager = EventManager(config, tmp_path / "events.log")
    await manager.start()
    yield manager
    await manager.stop()

@pytest_asyncio.fixture
async def plugin(plugin_metadata: Dict, event_manager: EventManager) -> Plugin:
    """Provide a configured plugin instance."""
    plugin = Plugin(plugin_metadata, event_manager)
    await plugin.start()
    yield plugin
    await plugin.stop()

@pytest.mark.asyncio
async def test_plugin_initialization(plugin: Plugin):
    """Test plugin initialization."""
    assert plugin.metadata["name"] == "{{ cookiecutter.plugin_name }}"
    assert plugin.metadata["version"] == "{{ cookiecutter.version }}"
    {% if cookiecutter.has_service == 'y' %}
    assert plugin.service_running
    {% endif %}

@pytest.mark.asyncio
async def test_plugin_shutdown(plugin: Plugin):
    """Test plugin shutdown."""
    await plugin.stop()
    {% if cookiecutter.has_service == 'y' %}
    assert not plugin.service_running
    {% endif %}

{% if cookiecutter.has_service == 'y' %}
@pytest.mark.asyncio
async def test_event_handling(plugin: Plugin, event_manager: EventManager):
    """Test event handling."""
    # Emit system shutdown event
    await event_manager.emit(Event.create("core:system:shutdown"))
    
    # Give time for event processing
    await asyncio.sleep(0.1)
    
    assert not plugin.service_running
{% endif %}

{% if cookiecutter.has_cli == 'y' %}
def test_cli_registration(plugin: Plugin):
    """Test CLI command registration."""
    # Mock CLI group
    class MockCLI:
        def group(self, name):
            assert name == "{{ cookiecutter.plugin_slug }}"
            def decorator(f):
                return f
            return decorator
    
    # Register commands
    plugin.register_cli_commands(MockCLI())
{% endif %}

{% if cookiecutter.has_filesystem == 'y' %}
def test_filesystem_mounting(plugin: Plugin, tmp_path: Path):
    """Test virtual filesystem mounting."""
    mount_point = tmp_path / "mount"
    mount_point.mkdir()
    
    plugin.mount_filesystem(mount_point)
    # Add filesystem-specific tests here
{% endif %}