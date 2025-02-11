"""
Plugin provider system for MetaRepos.
"""
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import git
import toml

logger = logging.getLogger(__name__)

@dataclass
class ProviderMetadata:
    """Metadata for a plugin provider."""
    name: str
    url: str
    branch: str = "main"
    plugins_path: str = "plugins"

class PluginProvider:
    """Manages plugin providers and their repositories."""
    
    def __init__(self, providers_dir: Path):
        self.providers_dir = providers_dir
        self.providers: Dict[str, ProviderMetadata] = {}
        
        # Create providers directory if it doesn't exist
        self.providers_dir.mkdir(parents=True, exist_ok=True)
    
    def add_provider(self, metadata: ProviderMetadata) -> bool:
        """Add a new plugin provider."""
        try:
            provider_dir = self.providers_dir / metadata.name
            
            # Clone the repository if it doesn't exist
            if not provider_dir.exists():
                logger.info(f"Cloning provider repository: {metadata.url}")
                git.Repo.clone_from(
                    metadata.url,
                    provider_dir,
                    branch=metadata.branch
                )
            
            self.providers[metadata.name] = metadata
            return True
        
        except Exception as e:
            logger.error(f"Failed to add provider {metadata.name}: {e}")
            return False
    
    def remove_provider(self, provider_name: str) -> bool:
        """Remove a plugin provider."""
        if provider_name not in self.providers:
            logger.warning(f"Provider not found: {provider_name}")
            return False
        
        try:
            provider_dir = self.providers_dir / provider_name
            if provider_dir.exists():
                # Remove the provider directory
                subprocess.run(["rm", "-rf", str(provider_dir)], check=True)
            
            del self.providers[provider_name]
            return True
        
        except Exception as e:
            logger.error(f"Failed to remove provider {provider_name}: {e}")
            return False
    
    def update_provider(self, provider_name: str) -> bool:
        """Update a plugin provider's repository."""
        if provider_name not in self.providers:
            logger.warning(f"Provider not found: {provider_name}")
            return False
        
        try:
            provider_dir = self.providers_dir / provider_name
            if not provider_dir.exists():
                logger.error(f"Provider directory not found: {provider_name}")
                return False
            
            # Update the repository
            repo = git.Repo(provider_dir)
            origin = repo.remotes.origin
            origin.pull()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to update provider {provider_name}: {e}")
            return False
    
    def get_plugin_paths(self) -> List[Path]:
        """Get paths to all plugin directories from all providers."""
        plugin_paths = []
        
        for provider_name, metadata in self.providers.items():
            provider_dir = self.providers_dir / provider_name
            plugins_dir = provider_dir / metadata.plugins_path
            
            if plugins_dir.exists():
                plugin_paths.append(plugins_dir)
        
        return plugin_paths
    
    def load_provider_config(self, config_file: Path) -> None:
        """Load provider configuration from a file."""
        try:
            if not config_file.exists():
                return
            
            data = toml.load(config_file)
            providers = data.get("providers", {})
            
            for name, provider_data in providers.items():
                metadata = ProviderMetadata(
                    name=name,
                    url=provider_data["url"],
                    branch=provider_data.get("branch", "main"),
                    plugins_path=provider_data.get("plugins_path", "plugins")
                )
                self.add_provider(metadata)
        
        except Exception as e:
            logger.error(f"Failed to load provider config: {e}")
    
    def save_provider_config(self, config_file: Path) -> None:
        """Save provider configuration to a file."""
        try:
            data = {"providers": {}}
            
            for name, metadata in self.providers.items():
                data["providers"][name] = {
                    "url": metadata.url,
                    "branch": metadata.branch,
                    "plugins_path": metadata.plugins_path
                }
            
            with open(config_file, "w") as f:
                toml.dump(data, f)
        
        except Exception as e:
            logger.error(f"Failed to save provider config: {e}")