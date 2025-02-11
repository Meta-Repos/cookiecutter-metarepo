"""
Plugin management system for MetaRepos.

This package provides the core plugin functionality including:
- Plugin discovery and loading
- Plugin lifecycle management
- Plugin configuration handling
"""

from .loader import PluginLoader
from .manager import PluginManager
from .provider import PluginProvider

__all__ = [
    'PluginLoader',
    'PluginManager',
    'PluginProvider',
]