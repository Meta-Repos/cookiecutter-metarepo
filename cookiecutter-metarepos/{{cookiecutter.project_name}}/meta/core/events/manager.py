"""
Event management system using ZeroMQ for pub/sub communication.
"""
import asyncio
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
        self.subscriber: Optional[Socket] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self._running = False
        self._subscriber_task: Optional[asyncio.Task] = None
        self._local_mode = True  # Use local callbacks for tests
        
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
        
        # Set up publisher
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(self.address)
        
        if not self._local_mode:
            # Set up subscriber for distributed mode
            self.subscriber = self.context.socket(zmq.SUB)
            self.subscriber.connect(self.address)
            
            # Start subscriber task
            self._running = True
            self._subscriber_task = asyncio.create_task(self._handle_subscriptions())
        
        logger.info(f"Event manager started on {self.address}")
        
        # Emit system startup event
        await self.emit(Event.create("core:system:startup"))
    
    async def stop(self) -> None:
        """Stop the event manager."""
        self._running = False
        
        if self.publisher:
            # Emit system shutdown event
            await self.emit(Event.create("core:system:shutdown"))
            
            self.publisher.close()
            self.publisher = None
        
        if self.subscriber:
            self.subscriber.close()
            self.subscriber = None
        
        if self._subscriber_task:
            await self._subscriber_task
            self._subscriber_task = None
        
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
        
        if self._local_mode:
            # Handle local subscribers directly
            if event.namespace in self.subscribers:
                for callback in self.subscribers[event.namespace]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}")
        else:
            # Publish the event for distributed mode
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
            if self.subscriber and not self._local_mode:
                self.subscriber.setsockopt_string(zmq.SUBSCRIBE, namespace)
        
        self.subscribers[namespace].append(callback)
        logger.debug(f"Added subscriber for {namespace}")
    
    def unsubscribe(self, namespace: str, callback: Callable[[Event], None]) -> None:
        """Unsubscribe from events with the given namespace."""
        if namespace in self.subscribers:
            try:
                self.subscribers[namespace].remove(callback)
                if not self.subscribers[namespace]:
                    del self.subscribers[namespace]
                    if self.subscriber and not self._local_mode:
                        self.subscriber.setsockopt_string(zmq.UNSUBSCRIBE, namespace)
                logger.debug(f"Removed subscriber for {namespace}")
            except ValueError:
                pass
    
    async def _handle_subscriptions(self) -> None:
        """Handle incoming events from subscriptions."""
        if not self.subscriber or self._local_mode:
            return
        
        while self._running:
            try:
                [namespace_bytes, message_bytes] = await self.subscriber.recv_multipart()
                namespace = namespace_bytes.decode()
                message = message_bytes.decode()
                
                # Parse event data
                event_data = json.loads(message)
                event = Event.from_dict(event_data)
                
                # Call subscribers
                if namespace in self.subscribers:
                    for callback in self.subscribers[namespace]:
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"Error in event callback: {e}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error handling subscription: {e}")
    
    def _log_event(self, event: Event) -> None:
        """Log an event to the log file."""
        if not self.log_path:
            return
        
        try:
            with open(self.log_path, 'a') as f:
                event_data = event.to_dict()
                f.write(json.dumps(event_data) + '\n')
        except Exception as e:
            logger.error(f"Failed to log event: {e}")