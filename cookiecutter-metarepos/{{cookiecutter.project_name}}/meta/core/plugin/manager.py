"""
Plugin management system for MetaRepos.
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from ..events import Event, EventManager
from .loader import PluginLoader, PluginMetadata

logger = logging.getLogger(__name__)

class Plugin:
    """Base class for MetaRepos plugins."""
    
    def __init__(self, metadata: PluginMetadata, event_manager: EventManager):
        self.metadata = metadata
        self.event_manager = event_manager
        self.running = False
    
    async def start(self) -> None:
        """Start the plugin."""
        self.running = True
    
    async def stop(self) -> None:
        """Stop the plugin."""
        self.running = False

class PluginManager:
    """Manages plugin lifecycle and configuration."""
    
    def __init__(
        self,
        plugin_paths: List[Path],
        event_manager: EventManager,
        config: Dict
    ):
        self.plugin_paths = plugin_paths
        self.event_manager = event_manager
        self.config = config
        self.loader = PluginLoader(plugin_paths)
        
        # Plugin storage
        self.available_plugins: Dict[str, PluginMetadata] = {}
        self.loaded_plugins: Dict[str, Type[Plugin]] = {}
        self.running_plugins: Dict[str, Plugin] = {}
    
    async def initialize(self) -> None:
        """Initialize the plugin manager."""
        # Discover available plugins
        self.available_plugins = self.loader.discover_plugins()
        
        # Load enabled plugins
        enabled_plugins = self.config.get("plugins", {}).get("enabled", [])
        for plugin_name in enabled_plugins:
            if plugin_name in self.available_plugins:
                await self.load_plugin(plugin_name)
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name."""
        if plugin_name not in self.available_plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        metadata = self.available_plugins[plugin_name]
        
        # Find the plugin directory
        plugin_dir = None
        for path in self.plugin_paths:
            candidate = path / plugin_name
            if candidate.exists():
                plugin_dir = candidate
                break
        
        if not plugin_dir:
            logger.error(f"Plugin directory not found: {plugin_name}")
            return False
        
        # Load the plugin class
        plugin_class = self.loader.load_plugin(plugin_dir, metadata)
        if not plugin_class:
            return False
        
        self.loaded_plugins[plugin_name] = plugin_class
        
        # Emit plugin loaded event
        await self.event_manager.emit(
            Event.create(
                "core:plugin:loaded",
                payload={"plugin_name": plugin_name}
            )
        )
        
        return True
    
    async def start_plugin(self, plugin_name: str) -> bool:
        """Start a loaded plugin."""
        if plugin_name not in self.loaded_plugins:
            logger.error(f"Plugin not loaded: {plugin_name}")
            return False
        
        if plugin_name in self.running_plugins:
            logger.warning(f"Plugin already running: {plugin_name}")
            return True
        
        try:
            plugin_class = self.loaded_plugins[plugin_name]
            metadata = self.available_plugins[plugin_name]
            
            plugin = plugin_class(metadata, self.event_manager)
            await plugin.start()
            
            self.running_plugins[plugin_name] = plugin
            
            # Emit plugin enabled event
            await self.event_manager.emit(
                Event.create(
                    "core:plugin:enabled",
                    payload={"plugin_name": plugin_name}
                )
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to start plugin {plugin_name}: {e}")
            return False
    
    async def stop_plugin(self, plugin_name: str) -> bool:
        """Stop a running plugin."""
        if plugin_name not in self.running_plugins:
            logger.warning(f"Plugin not running: {plugin_name}")
            return True
        
        try:
            plugin = self.running_plugins[plugin_name]
            await plugin.stop()
            
            del self.running_plugins[plugin_name]
            
            # Emit plugin disabled event
            await self.event_manager.emit(
                Event.create(
                    "core:plugin:disabled",
                    payload={"plugin_name": plugin_name}
                )
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop plugin {plugin_name}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.running_plugins:
            await self.stop_plugin(plugin_name)
        
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]
            
            # Emit plugin unloaded event
            await self.event_manager.emit(
                Event.create(
                    "core:plugin:unloaded",
                    payload={"plugin_name": plugin_name}
                )
            )
        
        return True
    
    async def shutdown(self) -> None:
        """Shutdown all running plugins."""
        for plugin_name in list(self.running_plugins.keys()):
            await self.stop_plugin(plugin_name)