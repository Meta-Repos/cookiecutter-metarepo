"""
Plugin loading and discovery for MetaRepos.
"""
import importlib.util
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Type

import toml

from .schema import ConfigSchema, ValidationError, create_schema

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    """Metadata for a MetaRepos plugin."""
    name: str
    version: str
    author: str
    description: str
    entry_point: str
    config_schema: Optional[ConfigSchema] = None
    has_service: bool = False
    has_cli: bool = False
    has_filesystem: bool = False

class PluginLoader:
    """Handles plugin discovery and loading."""
    
    def __init__(self, plugin_paths: List[Path]):
        self.plugin_paths = plugin_paths
        self.loaded_plugins: Dict[str, PluginMetadata] = {}
    
    def discover_plugins(self) -> Dict[str, PluginMetadata]:
        """
        Discover available plugins in the plugin paths.
        Returns a dictionary of plugin names to metadata.
        """
        discovered = {}
        
        for path in self.plugin_paths:
            if not path.exists():
                logger.warning(f"Plugin path does not exist: {path}")
                continue
            
            for plugin_dir in path.iterdir():
                if not plugin_dir.is_dir():
                    continue
                
                metadata = self._load_plugin_metadata(plugin_dir)
                if metadata:
                    discovered[metadata.name] = metadata
        
        return discovered
    
    def _load_plugin_metadata(self, plugin_dir: Path) -> Optional[PluginMetadata]:
        """Load plugin metadata from plugin.toml file."""
        metadata_file = plugin_dir / "plugin.toml"
        if not metadata_file.exists():
            return None
        
        try:
            data = toml.load(metadata_file)
            required_fields = ["name", "version", "author", "description", "entry_point"]
            
            if not all(field in data for field in required_fields):
                logger.error(f"Missing required fields in {metadata_file}")
                return None
            
            # Load configuration schema if present
            config_schema = None
            if "config_schema" in data:
                try:
                    config_schema = create_schema(data["config_schema"])
                except Exception as e:
                    logger.error(f"Failed to load config schema from {metadata_file}: {e}")
                    return None
            
            return PluginMetadata(
                name=data["name"],
                version=data["version"],
                author=data["author"],
                description=data["description"],
                entry_point=data["entry_point"],
                config_schema=config_schema,
                has_service=data.get("has_service", False),
                has_cli=data.get("has_cli", False),
                has_filesystem=data.get("has_filesystem", False)
            )
        except Exception as e:
            logger.error(f"Failed to load plugin metadata from {metadata_file}: {e}")
            return None
    
    def validate_plugin_config(self, metadata: PluginMetadata, config: Dict) -> Dict:
        """
        Validate plugin configuration against its schema.
        Returns validated configuration with defaults applied.
        """
        if not metadata.config_schema:
            # If no schema is defined, return config as-is
            return config
        
        try:
            return metadata.config_schema.validate(config)
        except ValidationError as e:
            logger.error(f"Configuration validation failed for plugin {metadata.name}: {e}")
            raise
    
    def load_plugin(self, plugin_dir: Path, metadata: PluginMetadata) -> Optional[Type]:
        """
        Load a plugin module from the given directory.
        Returns the plugin class if successful, None otherwise.
        """
        try:
            # Construct the full path to the entry point
            entry_point = plugin_dir / metadata.entry_point
            
            if not entry_point.exists():
                logger.error(f"Plugin entry point not found: {entry_point}")
                return None
            
            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"metarepos_plugin_{metadata.name}",
                entry_point
            )
            if not spec or not spec.loader:
                logger.error(f"Failed to create module spec for {entry_point}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a class named Plugin
            if not hasattr(module, "Plugin"):
                logger.error(f"No Plugin class found in {entry_point}")
                return None
            
            return module.Plugin
        
        except Exception as e:
            logger.error(f"Failed to load plugin {metadata.name}: {e}")
            return None