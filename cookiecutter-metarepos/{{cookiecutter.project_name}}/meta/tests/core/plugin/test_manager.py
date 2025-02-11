"""Tests for the plugin management system."""
import asyncio
import pytest
from pathlib import Path
from typing import Dict, List, Type
from unittest.mock import AsyncMock, MagicMock, patch

from meta.core.events import Event, EventManager
from meta.core.plugin.manager import Plugin, PluginManager
from meta.core.plugin.loader import PluginLoader, PluginMetadata

# Test fixtures
@pytest.fixture
def event_manager():
    """Create a mock event manager."""
    manager = AsyncMock(spec=EventManager)
    manager.emit = AsyncMock()
    return manager

@pytest.fixture
def plugin_metadata():
    """Create sample plugin metadata."""
    return PluginMetadata(
        name="test_plugin",
        version="1.0.0",
        description="Test plugin",
        entry_point="plugin.TestPlugin"
    )

@pytest.fixture
def mock_plugin_class(plugin_metadata, event_manager):
    """Create a mock plugin class."""
    class TestPlugin(Plugin):
        def __init__(self, metadata, event_manager):
            super().__init__(metadata, event_manager)
            self.started = False
            self.stopped = False

        async def start(self):
            await super().start()
            self.started = True

        async def stop(self):
            await super().stop()
            self.stopped = True

    return TestPlugin

@pytest.fixture
def plugin_paths(tmp_path):
    """Create temporary plugin paths."""
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    return [plugin_dir]

@pytest.fixture
def config():
    """Create sample configuration."""
    return {
        "plugins": {
            "enabled": ["test_plugin"]
        }
    }

@pytest.fixture
def plugin_manager(plugin_paths, event_manager, config):
    """Create a plugin manager instance."""
    return PluginManager(plugin_paths, event_manager, config)

# Lifecycle Tests
async def test_initialize_discovers_and_loads_plugins(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test plugin manager initialization process."""
    # Mock plugin discovery
    plugin_manager.loader.discover_plugins = MagicMock(
        return_value={"test_plugin": plugin_metadata}
    )
    
    # Mock plugin loading
    plugin_manager.loader.load_plugin = MagicMock(return_value=mock_plugin_class)
    
    await plugin_manager.initialize()
    
    # Verify plugin discovery
    assert "test_plugin" in plugin_manager.available_plugins
    
    # Verify plugin loading
    assert "test_plugin" in plugin_manager.loaded_plugins
    
    # Verify event emission
    plugin_manager.event_manager.emit.assert_called_with(
        Event.create(
            "core:plugin:loaded",
            payload={"plugin_name": "test_plugin"}
        )
    )

async def test_load_plugin_success(
    plugin_manager, plugin_paths, plugin_metadata, mock_plugin_class
):
    """Test successful plugin loading."""
    # Setup plugin directory
    plugin_dir = plugin_paths[0] / "test_plugin"
    plugin_dir.mkdir()
    
    # Mock plugin discovery and loading
    plugin_manager.available_plugins = {"test_plugin": plugin_metadata}
    plugin_manager.loader.load_plugin = MagicMock(return_value=mock_plugin_class)
    
    # Load plugin
    result = await plugin_manager.load_plugin("test_plugin")
    
    assert result is True
    assert "test_plugin" in plugin_manager.loaded_plugins
    plugin_manager.event_manager.emit.assert_called_once()

async def test_start_plugin_success(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test successful plugin starting."""
    # Setup loaded plugin
    plugin_manager.available_plugins = {"test_plugin": plugin_metadata}
    plugin_manager.loaded_plugins = {"test_plugin": mock_plugin_class}
    
    # Start plugin
    result = await plugin_manager.start_plugin("test_plugin")
    
    assert result is True
    assert "test_plugin" in plugin_manager.running_plugins
    plugin = plugin_manager.running_plugins["test_plugin"]
    assert plugin.started is True
    assert plugin.running is True
    plugin_manager.event_manager.emit.assert_called_once()

async def test_stop_plugin_success(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test successful plugin stopping."""
    # Setup running plugin
    plugin = mock_plugin_class(plugin_metadata, plugin_manager.event_manager)
    plugin_manager.running_plugins = {"test_plugin": plugin}
    
    # Stop plugin
    result = await plugin_manager.stop_plugin("test_plugin")
    
    assert result is True
    assert "test_plugin" not in plugin_manager.running_plugins
    assert plugin.stopped is True
    assert plugin.running is False
    plugin_manager.event_manager.emit.assert_called_once()

async def test_unload_plugin_success(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test successful plugin unloading."""
    # Setup loaded and running plugin
    plugin = mock_plugin_class(plugin_metadata, plugin_manager.event_manager)
    plugin_manager.loaded_plugins = {"test_plugin": mock_plugin_class}
    plugin_manager.running_plugins = {"test_plugin": plugin}
    
    # Unload plugin
    result = await plugin_manager.unload_plugin("test_plugin")
    
    assert result is True
    assert "test_plugin" not in plugin_manager.loaded_plugins
    assert "test_plugin" not in plugin_manager.running_plugins
    assert plugin.stopped is True
    # Should emit both disabled and unloaded events
    assert plugin_manager.event_manager.emit.call_count == 2

# Error Case Tests
async def test_load_plugin_not_found(plugin_manager):
    """Test loading non-existent plugin."""
    result = await plugin_manager.load_plugin("nonexistent_plugin")
    assert result is False
    plugin_manager.event_manager.emit.assert_not_called()

async def test_start_plugin_not_loaded(plugin_manager):
    """Test starting unloaded plugin."""
    result = await plugin_manager.start_plugin("test_plugin")
    assert result is False
    plugin_manager.event_manager.emit.assert_not_called()

async def test_start_plugin_already_running(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test starting already running plugin."""
    # Setup running plugin
    plugin = mock_plugin_class(plugin_metadata, plugin_manager.event_manager)
    plugin_manager.loaded_plugins = {"test_plugin": mock_plugin_class}
    plugin_manager.running_plugins = {"test_plugin": plugin}
    
    result = await plugin_manager.start_plugin("test_plugin")
    assert result is True  # Should succeed but not start again
    assert len(plugin_manager.running_plugins) == 1
    plugin_manager.event_manager.emit.assert_not_called()

async def test_stop_plugin_not_running(plugin_manager):
    """Test stopping non-running plugin."""
    result = await plugin_manager.stop_plugin("test_plugin")
    assert result is True  # Should succeed as plugin is already stopped
    plugin_manager.event_manager.emit.assert_not_called()

async def test_start_plugin_error(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test plugin start failure."""
    # Setup plugin that raises on start
    class ErrorPlugin(mock_plugin_class):
        async def start(self):
            raise RuntimeError("Start failed")
    
    plugin_manager.loaded_plugins = {"test_plugin": ErrorPlugin}
    plugin_manager.available_plugins = {"test_plugin": plugin_metadata}
    
    result = await plugin_manager.start_plugin("test_plugin")
    assert result is False
    assert "test_plugin" not in plugin_manager.running_plugins
    plugin_manager.event_manager.emit.assert_not_called()

async def test_stop_plugin_error(
    plugin_manager, plugin_metadata, mock_plugin_class
):
    """Test plugin stop failure."""
    # Setup plugin that raises on stop
    class ErrorPlugin(mock_plugin_class):
        async def stop(self):
            raise RuntimeError("Stop failed")
    
    plugin = ErrorPlugin(plugin_metadata, plugin_manager.event_manager)
    plugin_manager.running_plugins = {"test_plugin": plugin}
    
    result = await plugin_manager.stop_plugin("test_plugin")
    assert result is False
    assert "test_plugin" in plugin_manager.running_plugins
    plugin_manager.event_manager.emit.assert_not_called()

async def test_shutdown(plugin_manager, plugin_metadata, mock_plugin_class):
    """Test manager shutdown stops all plugins."""
    # Setup multiple running plugins
    plugins = {}
    for name in ["plugin1", "plugin2"]:
        plugin = mock_plugin_class(plugin_metadata, plugin_manager.event_manager)
        plugins[name] = plugin
    
    plugin_manager.running_plugins = plugins
    
    await plugin_manager.shutdown()
    
    assert len(plugin_manager.running_plugins) == 0
    for plugin in plugins.values():
        assert plugin.stopped is True
        assert plugin.running is False
    
    # Should emit disabled event for each plugin
    assert plugin_manager.event_manager.emit.call_count == 2