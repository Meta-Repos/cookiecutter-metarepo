"""
Event management system using ZeroMQ for pub/sub communication.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse

import zmq
from zmq.asyncio import Context, Socket

from .schema import Event, validate_event_namespace

logger = logging.getLogger(__name__)

class EventManager:
    """Manages event distribution using ZeroMQ pub/sub system."""
    
    def __init__(
        self,
        config: Dict,
        log_path: Optional[Path] = None
    ):
        self.config = config.get("events", {})
        self.host = self.config.get("host", "127.0.0.1")
        self.port = self.config.get("port", 5555)
        self.protocol = self.config.get("protocol", "tcp")
        
        # Construct the ZMQ address
        if self.protocol == "tcp":
            self.address = f"tcp://{self.host}:{self.port}"
        elif self.protocol == "ipc":
            self.address = f"ipc:///tmp/metarepos-events-{self.port}"
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
        
        self.log_path = log_path
        self.context: Optional[Context] = None
        self.publisher: Optional[Socket] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Set up logging
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
    
    async def start(self) -> None:
        """Start the event manager."""
        self.context = Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(self.address)
        logger.info(f"Event manager started on {self.address}")
        
        # Emit system startup event
        await self.emit(Event.create("core:system:startup"))
    
    async def stop(self) -> None:
        """Stop the event manager."""
        if self.publisher:
            # Emit system shutdown event
            await self.emit(Event.create("core:system:shutdown"))
            
            self.publisher.close()
            self.publisher = None
        
        if self.context:
            self.context.term()
            self.context = None
        
        logger.info("Event manager stopped")
    
    async def emit(self, event: Event) -> None:
        """Emit an event to all subscribers."""
        if not self.publisher:
            raise RuntimeError("Event manager not started")
        
        if not validate_event_namespace(event.namespace):
            raise ValueError(f"Invalid event namespace: {event.namespace}")
        
        # Serialize the event
        event_data = event.to_dict()
        message = json.dumps(event_data)
        
        # Publish the event
        await self.publisher.send_multipart([
            event.namespace.encode(),
            message.encode()
        ])
        
        # Log the event
        if self.log_path:
            self._log_event(event)
        
        logger.debug(f"Emitted event: {event.namespace}")
    
    def subscribe(self, namespace: str, callback: Callable[[Event], None]) -> None:
        """Subscribe to events with the given namespace."""
        if not validate_event_namespace(namespace):
            raise ValueError(f"Invalid event namespace: {namespace}")
        
        if namespace not in self.subscribers:
            self.subscribers[namespace] = []
        
        self.subscribers[namespace].append(callback)
        logger.debug(f"Added subscriber for {namespace}")
    
    def unsubscribe(self, namespace: str, callback: Callable[[Event], None]) -> None:
        """Unsubscribe from events with the given namespace."""
        if namespace in self.subscribers:
            try:
                self.subscribers[namespace].remove(callback)
                if not self.subscribers[namespace]:
                    del self.subscribers[namespace]
                logger.debug(f"Removed subscriber for {namespace}")
            except ValueError:
                pass
    
    def _log_event(self, event: Event) -> None:
        """Log an event to the log file."""
        if not self.log_path:
            return
        
        with open(self.log_path, 'a') as f:
            event_data = event.to_dict()
            f.write(json.dumps(event_data) + '\n')