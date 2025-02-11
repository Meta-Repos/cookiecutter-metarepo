"""
Tests for event schema functionality.
"""
from datetime import datetime

import pytest

from ....core.events.schema import Event, validate_event_namespace

def test_event_creation():
    """Test basic event creation."""
    event = Event(
        namespace="test:event:created",
        timestamp=datetime.utcnow(),
        metadata={"test": "metadata"},
        payload={"test": "payload"}
    )
    
    assert event.namespace == "test:event:created"
    assert isinstance(event.timestamp, datetime)
    assert event.metadata == {"test": "metadata"}
    assert event.payload == {"test": "payload"}

def test_event_create_helper():
    """Test the create helper method."""
    event = Event.create(
        namespace="test:event:created",
        metadata={"test": "metadata"},
        payload={"test": "payload"}
    )
    
    assert event.namespace == "test:event:created"
    assert isinstance(event.timestamp, datetime)
    assert event.metadata == {"test": "metadata"}
    assert event.payload == {"test": "payload"}

def test_event_serialization():
    """Test event serialization to and from dict."""
    original = Event.create(
        namespace="test:event:created",
        metadata={"test": "metadata"},
        payload={"test": "payload"}
    )
    
    # Convert to dict
    event_dict = original.to_dict()
    
    # Convert back to event
    restored = Event.from_dict(event_dict)
    
    assert restored.namespace == original.namespace
    assert restored.timestamp.isoformat() == original.timestamp.isoformat()
    assert restored.metadata == original.metadata
    assert restored.payload == original.payload

def test_validate_event_namespace():
    """Test event namespace validation."""
    # Valid namespaces
    assert validate_event_namespace("core:system:start")
    assert validate_event_namespace("plugin:test:event")
    assert validate_event_namespace("test:event:created")
    
    # Invalid namespaces
    assert not validate_event_namespace("invalid")
    assert not validate_event_namespace("invalid:namespace")
    assert not validate_event_namespace("too:many:parts:here")
    assert not validate_event_namespace("invalid:name$space:here")
    assert not validate_event_namespace(":empty:parts:")

def test_event_without_optional_fields():
    """Test event creation without optional fields."""
    event = Event(
        namespace="test:event:created",
        timestamp=datetime.utcnow()
    )
    
    assert event.namespace == "test:event:created"
    assert isinstance(event.timestamp, datetime)
    assert event.metadata == {}
    assert event.payload == {}

def test_event_with_empty_fields():
    """Test event creation with empty optional fields."""
    event = Event(
        namespace="test:event:created",
        timestamp=datetime.utcnow(),
        metadata={},
        payload={}
    )
    
    assert event.namespace == "test:event:created"
    assert isinstance(event.timestamp, datetime)
    assert event.metadata == {}
    assert event.payload == {}

def test_invalid_event_namespace():
    """Test event creation with invalid namespace."""
    with pytest.raises(ValueError):
        Event.create("invalid:namespace")