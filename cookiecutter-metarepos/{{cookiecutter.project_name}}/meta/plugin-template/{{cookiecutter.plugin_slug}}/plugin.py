"""
{{ cookiecutter.plugin_description }}
"""
import logging
from pathlib import Path
from typing import Dict, Optional

from metarepos.core.events import Event, EventManager
from metarepos.core.plugin import Plugin

logger = logging.getLogger(__name__)

class Plugin(Plugin):
    """{{ cookiecutter.plugin_name }} plugin implementation."""
    
    def __init__(self, metadata: Dict, event_manager: EventManager):
        super().__init__(metadata, event_manager)
        self.config = metadata.get("config", {})
        {% if cookiecutter.has_service == 'y' %}
        # Initialize service-specific attributes
        self.service_running = False
        {% endif %}
    
    async def start(self) -> None:
        """Start the plugin."""
        await super().start()
        {% if cookiecutter.has_service == 'y' %}
        # Start the service
        try:
            self.service_running = True
            logger.info("{{ cookiecutter.plugin_name }} service started")
            
            # Subscribe to relevant events
            self.event_manager.subscribe("core:system:shutdown", self._handle_shutdown)
            
            # Emit service started event
            await self.event_manager.emit(
                Event.create(
                    f"plugin:{{ cookiecutter.plugin_slug }}:started",
                    metadata={"version": self.metadata["version"]}
                )
            )
        except Exception as e:
            logger.error(f"Failed to start {{ cookiecutter.plugin_name }} service: {e}")
            self.service_running = False
        {% endif %}
    
    async def stop(self) -> None:
        """Stop the plugin."""
        {% if cookiecutter.has_service == 'y' %}
        # Stop the service
        if self.service_running:
            try:
                self.service_running = False
                logger.info("{{ cookiecutter.plugin_name }} service stopped")
                
                # Emit service stopped event
                await self.event_manager.emit(
                    Event.create(
                        f"plugin:{{ cookiecutter.plugin_slug }}:stopped"
                    )
                )
            except Exception as e:
                logger.error(f"Error stopping {{ cookiecutter.plugin_name }} service: {e}")
        {% endif %}
        await super().stop()
    {% if cookiecutter.has_service == 'y' %}
    
    async def _handle_shutdown(self, event: Event) -> None:
        """Handle system shutdown event."""
        if self.service_running:
            await self.stop()
    {% endif %}
    {% if cookiecutter.has_cli == 'y' %}
    
    def register_cli_commands(self, cli) -> None:
        """Register CLI commands for this plugin."""
        @cli.group("{{ cookiecutter.plugin_slug }}")
        def plugin_cli():
            """{{ cookiecutter.plugin_name }} commands."""
            pass
        
        @plugin_cli.command()
        def status():
            """Show plugin status."""
            {% if cookiecutter.has_service == 'y' %}
            if self.service_running:
                cli.console.print("[green]Service is running[/green]")
            else:
                cli.console.print("[red]Service is not running[/red]")
            {% else %}
            cli.console.print("Plugin is enabled")
            {% endif %}
    {% endif %}
    {% if cookiecutter.has_filesystem == 'y' %}
    
    def mount_filesystem(self, mount_point: Path) -> None:
        """Mount the plugin's virtual filesystem."""
        # TODO: Implement virtual filesystem mounting
        pass
    {% endif %}