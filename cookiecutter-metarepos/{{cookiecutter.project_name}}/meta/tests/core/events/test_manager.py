"""
Tests for event manager functionality.
"""
import asyncio
from pathlib import Path
from typing import Dict

import pytest
import pytest_asyncio

from ....core.events import Event, EventManager

@pytest_asyncio.fixture
async def event_manager(test_config: Dict, temp_log_path: Path) -> EventManager:
    """Provide a configured event manager."""
    manager = EventManager(test_config, temp_log_path)
    await manager.start()
    yield manager
    await manager.stop()

@pytest.mark.asyncio
async def test_event_manager_startup(event_manager: EventManager):
    """Test event manager startup."""
    assert event_manager.publisher is not None
    assert event_manager.context is not None
    assert event_manager.address == f"tcp://{event_manager.host}:{event_manager.port}"

@pytest.mark.asyncio
async def test_event_emission(event_manager: EventManager, temp_log_path: Path):
    """Test event emission and logging."""
    # Create and emit an event
    event = Event.create(
        namespace="test:event:emitted",
        payload={"test": "data"}
    )
    await event_manager.emit(event)
    
    # Check that the event was logged
    assert temp_log_path.exists()
    log_content = temp_log_path.read_text()
    assert "test:event:emitted" in log_content
    assert "test" in log_content
    assert "data" in log_content

@pytest.mark.asyncio
async def test_event_subscription(event_manager: EventManager):
    """Test event subscription and callback execution."""
    received_events = []
    
    def callback(event: Event):
        received_events.append(event)
    
    # Subscribe to events
    event_manager.subscribe("test:event:received", callback)
    
    # Emit an event
    event = Event.create(
        namespace="test:event:received",
        payload={"test": "subscription"}
    )
    await event_manager.emit(event)
    
    # Give some time for the event to be processed
    await asyncio.sleep(0.1)
    
    # Check that the callback was executed
    assert len(received_events) == 1
    received = received_events[0]
    assert received.namespace == "test:event:received"
    assert received.payload == {"test": "subscription"}

@pytest.mark.asyncio
async def test_event_unsubscription(event_manager: EventManager):
    """Test event unsubscription."""
    received_events = []
    
    def callback(event: Event):
        received_events.append(event)
    
    # Subscribe and then unsubscribe
    event_manager.subscribe("test:event:unsubscribe", callback)
    event_manager.unsubscribe("test:event:unsubscribe", callback)
    
    # Emit an event
    event = Event.create(
        namespace="test:event:unsubscribe",
        payload={"test": "unsubscription"}
    )
    await event_manager.emit(event)
    
    # Give some time for the event to be processed
    await asyncio.sleep(0.1)
    
    # Check that no events were received
    assert len(received_events) == 0

@pytest.mark.asyncio
async def test_invalid_event_emission(event_manager: EventManager):
    """Test emission of events with invalid namespaces."""
    with pytest.raises(ValueError):
        await event_manager.emit(Event.create("invalid:namespace"))

@pytest.mark.asyncio
async def test_multiple_subscribers(event_manager: EventManager):
    """Test multiple subscribers for the same event."""
    received_1 = []
    received_2 = []
    
    def callback_1(event: Event):
        received_1.append(event)
    
    def callback_2(event: Event):
        received_2.append(event)
    
    # Subscribe both callbacks
    event_manager.subscribe("test:event:multiple", callback_1)
    event_manager.subscribe("test:event:multiple", callback_2)
    
    # Emit an event
    event = Event.create(
        namespace="test:event:multiple",
        payload={"test": "multiple"}
    )
    await event_manager.emit(event)
    
    # Give some time for the event to be processed
    await asyncio.sleep(0.1)
    
    # Check that both callbacks received the event
    assert len(received_1) == 1
    assert len(received_2) == 1
    assert received_1[0].payload == {"test": "multiple"}
    assert received_2[0].payload == {"test": "multiple"}

@pytest.mark.asyncio
async def test_event_manager_shutdown(test_config: Dict, temp_log_path: Path):
    """Test event manager shutdown."""
    manager = EventManager(test_config, temp_log_path)
    await manager.start()
    
    # Verify startup
    assert manager.publisher is not None
    assert manager.context is not None
    
    # Shutdown
    await manager.stop()
    
    # Verify shutdown
    assert manager.publisher is None
    assert manager.context is None