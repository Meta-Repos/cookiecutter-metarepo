"""
Tests for event logger functionality.
"""
import json
from datetime import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time

from core.events import Event, EventLogger

@pytest.fixture
def event_logger(tmp_path: Path) -> EventLogger:
    """Provide a configured event logger."""
    log_dir = tmp_path / "logs"
    return EventLogger(log_dir)

def test_logger_initialization(tmp_path: Path):
    """Test event logger initialization."""
    log_dir = tmp_path / "logs"
    logger = EventLogger(log_dir)
    
    assert log_dir.exists()
    assert logger.log_dir == log_dir

def test_event_logging(event_logger: EventLogger):
    """Test logging of events."""
    # Create and log an event
    event = Event.create(
        namespace="test:logger:event",
        payload={"test": "logging"}
    )
    event_logger.log_event(event)
    
    # Verify the log file exists and contains the event
    log_file = event_logger.current_log_file
    assert log_file.exists()
    
    # Read and verify the log content
    with open(log_file) as f:
        log_line = f.readline()
        log_data = json.loads(log_line)
        
        assert log_data["namespace"] == "test:logger:event"
        assert log_data["payload"] == {"test": "logging"}

def test_log_rotation(event_logger: EventLogger, monkeypatch):
    """Test log file rotation based on size."""
    # Set a small max size for testing
    monkeypatch.setattr(event_logger, "max_size", 100)
    
    # Create and log multiple events
    for i in range(10):
        event = Event.create(
            namespace="test:logger:rotation",
            payload={"iteration": i, "data": "x" * 50}  # Create large events
        )
        event_logger.log_event(event)
    
    # Check that rotation occurred
    log_dir = event_logger.log_dir
    backup_files = list(log_dir.glob("*.1"))
    assert len(backup_files) > 0

def test_recent_events_retrieval(event_logger: EventLogger):
    """Test retrieval of recent events."""
    # Log multiple events
    events = []
    for i in range(5):
        event = Event.create(
            namespace="test:logger:recent",
            payload={"iteration": i}
        )
        event_logger.log_event(event)
        events.append(event)
    
    # Retrieve recent events
    recent = event_logger.get_recent_events(count=3)
    
    assert len(recent) == 3
    assert recent[-1]["namespace"] == "test:logger:recent"
    assert recent[-1]["payload"]["iteration"] == 4

@freeze_time("2025-02-11")
def test_log_file_date_rotation(event_logger: EventLogger):
    """Test log file rotation based on date."""
    # Log an event on day 1
    event1 = Event.create(
        namespace="test:logger:day1",
        payload={"day": 1}
    )
    event_logger.log_event(event1)
    day1_file = event_logger.current_log_file
    
    # Move time forward one day
    with freeze_time("2025-02-12"):
        # Log an event on day 2
        event2 = Event.create(
            namespace="test:logger:day2",
            payload={"day": 2}
        )
        event_logger.log_event(event2)
        day2_file = event_logger.current_log_file
        
        assert day1_file != day2_file
        assert day1_file.exists()
        assert day2_file.exists()

def test_invalid_log_directory(tmp_path: Path):
    """Test logger behavior with invalid directory."""
    invalid_dir = tmp_path / "nonexistent" / "logs"
    logger = EventLogger(invalid_dir)
    
    # The directory should be created
    assert invalid_dir.exists()
    
    # Should be able to log events
    event = Event.create(
        namespace="test:logger:invalid",
        payload={"test": "invalid_dir"}
    )
    logger.log_event(event)
    
    assert logger.current_log_file.exists()

def test_concurrent_logging(event_logger: EventLogger):
    """Test logging multiple events in quick succession."""
    events = []
    for i in range(100):
        event = Event.create(
            namespace="test:logger:concurrent",
            payload={"iteration": i}
        )
        events.append(event)
    
    # Log all events
    for event in events:
        event_logger.log_event(event)
    
    # Verify all events were logged
    log_content = event_logger.current_log_file.read_text()
    assert len(log_content.splitlines()) == 100