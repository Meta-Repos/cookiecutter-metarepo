"""
Event schema definitions for MetaRepos.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class Event:
    """Base event class for MetaRepos events."""
    namespace: str
    timestamp: datetime
    metadata: Optional[Dict] = None
    payload: Optional[Dict] = None

    @classmethod
    def create(cls, namespace: str, payload: Optional[Dict] = None, metadata: Optional[Dict] = None) -> 'Event':
        """Create a new event with the current timestamp."""
        return cls(
            namespace=namespace,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            payload=payload or {}
        )

    def to_dict(self) -> Dict:
        """Convert the event to a dictionary for serialization."""
        return {
            "namespace": self.namespace,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
            "payload": self.payload or {}
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create an event from a dictionary."""
        return cls(
            namespace=data["namespace"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            payload=data.get("payload", {})
        )

# Core event namespaces
CORE_EVENTS = {
    # System events
    "core:system:startup": "System startup event",
    "core:system:shutdown": "System shutdown event",
    
    # Plugin events
    "core:plugin:loaded": "Plugin loaded event",
    "core:plugin:unloaded": "Plugin unloaded event",
    "core:plugin:enabled": "Plugin enabled event",
    "core:plugin:disabled": "Plugin disabled event",
    
    # File events
    "core:file:created": "File created event",
    "core:file:modified": "File modified event",
    "core:file:deleted": "File deleted event"
}

def validate_event_namespace(namespace: str) -> bool:
    """
    Validate an event namespace.
    
    Format: category:component:action
    Example: core:file:created
    """
    parts = namespace.split(":")
    if len(parts) != 3:
        return False
    
    if not all(part.isidentifier() for part in parts):
        return False
    
    return True