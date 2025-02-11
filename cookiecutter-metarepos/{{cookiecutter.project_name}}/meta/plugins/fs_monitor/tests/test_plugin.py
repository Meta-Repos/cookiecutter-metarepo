"""
Tests for the file system monitor plugin.
"""
import os
import time
from pathlib import Path
from typing import Dict, List

import pytest
from watchdog.observers import Observer

from core.events import Event
from plugins.fs_monitor.plugin import FSMonitorPlugin, MonorepoEventHandler

@pytest.fixture
def test_dir(tmp_path: Path) -> Path:
    """Provide a test directory."""
    return tmp_path / "test_repo"

@pytest.fixture
def plugin(test_dir: Path) -> FSMonitorPlugin:
    """Provide a configured plugin instance."""
    plugin = FSMonitorPlugin()
    
    # Create test directory
    test_dir.mkdir(exist_ok=True)
    os.chdir(test_dir)
    
    yield plugin
    
    # Cleanup
    plugin.stop()
    os.chdir("..")

@pytest.fixture
def received_events() -> List[Event]:
    """Track received events."""
    events = []
    return events

def test_plugin_initialization(plugin: FSMonitorPlugin):
    """Test plugin initialization."""
    assert plugin.observer is None
    assert plugin.event_handler is None
    assert not plugin.watch_paths

def test_plugin_start_stop(plugin: FSMonitorPlugin):
    """Test plugin start and stop."""
    # Start plugin
    plugin.start()
    assert isinstance(plugin.observer, Observer)
    assert isinstance(plugin.event_handler, MonorepoEventHandler)
    assert plugin.watch_paths
    assert plugin.observer.is_alive()
    
    # Stop plugin
    plugin.stop()
    assert plugin.observer is None
    assert plugin.event_handler is None
    assert not plugin.watch_paths

def test_file_creation_event(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test file creation event."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:created", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Create a file
    test_file = test_dir / "test.txt"
    test_file.write_text("test content")
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:fs_monitor:fs:created"
    assert event.payload["path"].endswith("test.txt")
    assert not event.payload["is_directory"]

def test_file_modification_event(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test file modification event."""
    # Create initial file
    test_file = test_dir / "test.txt"
    test_file.write_text("initial content")
    
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:modified", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Modify the file
    test_file.write_text("modified content")
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify event
    assert len(received_events) >= 1
    event = received_events[-1]
    assert event.namespace == "plugin:fs_monitor:fs:modified"
    assert event.payload["path"].endswith("test.txt")
    assert not event.payload["is_directory"]

def test_file_deletion_event(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test file deletion event."""
    # Create initial file
    test_file = test_dir / "test.txt"
    test_file.write_text("test content")
    
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:deleted", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Delete the file
    test_file.unlink()
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:fs_monitor:fs:deleted"
    assert event.payload["path"].endswith("test.txt")
    assert not event.payload["is_directory"]

def test_file_move_event(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test file move event."""
    # Create initial file
    src_file = test_dir / "source.txt"
    src_file.write_text("test content")
    dest_file = test_dir / "dest.txt"
    
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:moved", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Move the file
    src_file.rename(dest_file)
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:fs_monitor:fs:moved"
    assert event.payload["src_path"].endswith("source.txt")
    assert event.payload["dest_path"].endswith("dest.txt")
    assert not event.payload["is_directory"]

def test_directory_events(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test directory events."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:created", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Create a directory
    test_dir = test_dir / "test_dir"
    test_dir.mkdir()
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:fs_monitor:fs:created"
    assert event.payload["path"].endswith("test_dir")
    assert event.payload["is_directory"]

def test_ignore_patterns(plugin: FSMonitorPlugin, test_dir: Path, received_events: List[Event]):
    """Test ignore patterns."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:created", event_callback)
    
    # Start monitoring
    plugin.start()
    
    # Create ignored files
    (test_dir / "__pycache__").mkdir()
    (test_dir / "test.pyc").write_text("")
    (test_dir / ".git").mkdir()
    
    # Create non-ignored file
    (test_dir / "test.txt").write_text("")
    
    # Wait for event processing
    time.sleep(0.1)
    
    # Verify only non-ignored file event was received
    assert len(received_events) == 1
    event = received_events[0]
    assert event.payload["path"].endswith("test.txt")

def test_monitor_start_stop_events(plugin: FSMonitorPlugin, received_events: List[Event]):
    """Test monitor start/stop events."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:monitor:started", event_callback)
    plugin.event_manager.subscribe("plugin:fs_monitor:fs:monitor:stopped", event_callback)
    
    # Start and stop plugin
    plugin.start()
    plugin.stop()
    
    # Verify events
    assert len(received_events) == 2
    assert received_events[0].namespace == "plugin:fs_monitor:fs:monitor:started"
    assert received_events[1].namespace == "plugin:fs_monitor:fs:monitor:stopped"