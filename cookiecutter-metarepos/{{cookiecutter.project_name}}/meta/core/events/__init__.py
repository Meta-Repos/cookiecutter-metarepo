"""
Event management system for MetaRepos.

This package provides the core event management functionality including:
- Event schema definitions
- ZeroMQ-based pub/sub event distribution
- Event logging and rotation
"""

from .logger import EventLogger
from .manager import EventManager
from .schema import Event, CORE_EVENTS, validate_event_namespace

__all__ = [
    'Event',
    'EventLogger',
    'EventManager',
    'CORE_EVENTS',
    'validate_event_namespace',
]