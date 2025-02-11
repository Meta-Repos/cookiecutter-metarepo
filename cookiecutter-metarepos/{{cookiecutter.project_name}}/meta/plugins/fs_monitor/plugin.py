"""
File system monitor plugin for MetaRepos.

This plugin monitors the monorepo for file system changes and emits events.
"""
import os
import time
from pathlib import Path
from typing import Dict, Optional, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from core.events import Event
from core.plugin import Plugin

class MonorepoEventHandler(FileSystemEventHandler):
    """Handle file system events and emit corresponding MetaRepos events."""
    
    def __init__(self, plugin: 'FSMonitorPlugin'):
        self.plugin = plugin
        self.ignore_patterns: Set[str] = {
            '.git',
            '__pycache__',
            '*.pyc',
            '.coverage',
            '.pytest_cache',
            '.mypy_cache',
            '.venv',
            'node_modules',
            '.DS_Store'
        }
    
    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        path_parts = Path(path).parts
        return any(
            any(part.startswith(pattern.strip('*')) for part in path_parts)
            for pattern in self.ignore_patterns
        )
    
    def on_created(self, event: FileSystemEvent):
        """Handle file/directory creation events."""
        if self.should_ignore(event.src_path):
            return
        
        self.plugin.emit_event('fs:created', {
            'path': event.src_path,
            'is_directory': event.is_directory
        })
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file/directory deletion events."""
        if self.should_ignore(event.src_path):
            return
        
        self.plugin.emit_event('fs:deleted', {
            'path': event.src_path,
            'is_directory': event.is_directory
        })
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file/directory modification events."""
        if self.should_ignore(event.src_path):
            return
        
        self.plugin.emit_event('fs:modified', {
            'path': event.src_path,
            'is_directory': event.is_directory
        })
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file/directory move events."""
        if self.should_ignore(event.src_path) or self.should_ignore(event.dest_path):
            return
        
        self.plugin.emit_event('fs:moved', {
            'src_path': event.src_path,
            'dest_path': event.dest_path,
            'is_directory': event.is_directory
        })

class FSMonitorPlugin(Plugin):
    """Plugin for monitoring file system changes in the monorepo."""
    
    def __init__(self):
        super().__init__()
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[MonorepoEventHandler] = None
        self.watch_paths: Set[str] = set()
    
    def start(self):
        """Start the file system monitor."""
        self.observer = Observer()
        self.event_handler = MonorepoEventHandler(self)
        
        # Get watch paths from config
        config = self.get_config()
        watch_paths = config.get('watch_paths', ['.'])
        ignore_patterns = config.get('ignore_patterns', [])
        
        # Update ignore patterns
        if ignore_patterns:
            self.event_handler.ignore_patterns.update(ignore_patterns)
        
        # Set up watches
        for path in watch_paths:
            if os.path.exists(path):
                self.observer.schedule(
                    self.event_handler,
                    path,
                    recursive=True
                )
                self.watch_paths.add(path)
        
        # Start monitoring
        self.observer.start()
        self.emit_event('fs:monitor:started', {
            'watch_paths': list(self.watch_paths),
            'ignore_patterns': list(self.event_handler.ignore_patterns)
        })
    
    def stop(self):
        """Stop the file system monitor."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.event_handler = None
            self.watch_paths.clear()
            self.emit_event('fs:monitor:stopped', {})
    
    def get_config(self) -> Dict:
        """Get plugin configuration."""
        try:
            with open('plugin.toml') as f:
                import toml
                return toml.load(f)
        except Exception:
            return {}
    
    def emit_event(self, namespace: str, payload: Dict):
        """Emit a file system event."""
        event = Event.create(
            namespace=f'plugin:fs_monitor:{namespace}',
            payload=payload
        )
        self.event_manager.emit(event)