# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Overview

This monorepo is managed by MetaRepos, providing:

- 🔧 Plugin-based extensibility
- 📦 Event-driven architecture
- 🛠️ Command-line management
- 📝 Flexible configuration
- 🧪 Comprehensive testing
- 📚 Detailed documentation

## Architecture

### Event System

The event system provides a robust foundation for inter-component communication:

1. Event Manager
   - Handles event routing and delivery
   - Manages event subscriptions
   - Provides event filtering
   - Ensures event ordering
   - Handles error recovery

2. Event Flow
   ```
   [Publisher] → [Event Manager] → [Event Logger] → [Subscribers]
                      ↓
                [Event Schema]
                (validation)
   ```

3. Event Types
   - System events (startup, shutdown)
   - Plugin events (load, unload)
   - Custom events (user-defined)

4. Event Handling
   ```python
   from core.events import EventManager, Event

   # Subscribe to events
   @event_manager.subscribe("plugin.loaded")
   def handle_plugin_load(event: Event):
       plugin_name = event.data["name"]
       print(f"Plugin {plugin_name} loaded")

   # Publish events
   event_manager.publish(Event(
       type="plugin.loaded",
       data={"name": "my-plugin"}
   ))
   ```

### Plugin System

The plugin system enables extensible functionality:

1. Plugin Lifecycle
   ```
   [Discovery] → [Loading] → [Initialization] → [Running] → [Cleanup]
        ↑           ↓            ↓                ↓           ↓
   [Plugin Dir] [Validation] [Start Call]    [Operations] [Stop Call]
   ```

2. Plugin Components
   - Manager: Handles plugin lifecycle
   - Provider: Manages plugin discovery
   - Loader: Handles plugin loading
   - Schema: Defines plugin structure

3. Plugin Development
   ```python
   from core.plugin import Plugin
   from core.events import Event

   class MyPlugin(Plugin):
       def __init__(self):
           super().__init__()
           # Register event handlers
           self.subscribe("system.startup", self.handle_startup)
           
       def start(self):
           """Called when plugin is enabled"""
           # Initialize resources
           self.load_config()
           self.setup_handlers()
           
           # Publish plugin ready event
           self.publish(Event(
               type="plugin.ready",
               data={"name": self.name}
           ))
       
       def handle_startup(self, event: Event):
           """Handle system startup event"""
           print("System is starting up")
       
       def stop(self):
           """Called when plugin is disabled"""
           # Cleanup resources
           self.save_state()
           self.close_handlers()
   ```

4. Plugin Configuration
   ```toml
   # plugin.toml
   name = "my-plugin"
   version = "0.1.0"
   description = "My custom plugin"

   [settings]
   # Plugin-specific settings
   log_level = "info"
   cache_size = 1000
   
   [dependencies]
   # Other plugins this plugin depends on
   required = ["core-plugin", "util-plugin"]
   optional = ["extra-plugin"]
   ```

## Directory Structure

```
{{ cookiecutter.project_name }}/
├── meta/                 # MetaRepos management tool
│   ├── cli/             # CLI implementation
│   ├── core/            # Core functionality
│   │   ├── events/      # Event system
│   │   │   ├── manager.py   # Event routing and delivery
│   │   │   ├── logger.py    # Event logging
│   │   │   └── schema.py    # Event validation
│   │   └── plugin/      # Plugin system
│   │       ├── manager.py   # Plugin lifecycle
│   │       ├── provider.py  # Plugin discovery
│   │       ├── loader.py    # Plugin loading
│   │       └── schema.py    # Plugin validation
│   ├── plugins/         # Plugin directory
│   ├── tests/           # Test suite
│   ├── metarepo.toml    # Configuration file
│   └── pyproject.toml   # Package configuration
└── src/                 # Monorepo source code
    ├── data_model/      # Data models
    ├── docs/            # Documentation
    ├── libraries/       # Shared libraries
    └── projects/        # Project directories
```

## Installation

1. Create a virtual environment:
```bash
cd meta
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -e .[dev]
```

## Configuration

The system can be configured through multiple layers:

1. Configuration File (`meta/metarepo.toml`):
```toml
[core]
# Core system settings
log_level = "info"
event_log_path = "logs/events.log"

[events]
# Event system configuration
host = "127.0.0.1"
port = 5555
protocol = "tcp"  # tcp or ipc

[plugins]
# Plugin system settings
enabled = []          # Enabled plugins
search_paths = [      # Plugin search paths
    "plugins",
    "~/.metarepos/plugins"
]

# Plugin-specific settings
[plugins.my-plugin]
setting1 = "value1"
setting2 = "value2"
```

2. Environment Variables:
- `METAREPOS_CONFIG`: Path to configuration file
- `METAREPOS_PLUGIN_DIR`: Plugin directory location
- `METAREPOS_LOG_DIR`: Log directory location

3. Command-line Arguments:
```bash
metarepos --config path/to/config.toml
metarepos --plugin-dir path/to/plugins
metarepos --log-dir path/to/logs
```

## Usage

### Basic Commands
```bash
# Show help
metarepos --help

# Check health status
metarepos health

# Show monorepo status
metarepos status
```

### Plugin Management
```bash
# List installed plugins
metarepos plugin list

# Install a plugin
metarepos plugin install <plugin>

# Uninstall a plugin
metarepos plugin uninstall <plugin>

# Enable a plugin
metarepos plugin enable <plugin>

# Disable a plugin
metarepos plugin disable <plugin>
```

## Plugin Development

1. Create a new plugin:
```bash
cd meta/plugins
mkdir my-plugin
cd my-plugin
```

2. Create plugin files:
```python
# plugin.py
from core.plugin import Plugin
from core.events import Event

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.subscribe("system.startup", self.handle_startup)
    
    def start(self):
        """Plugin initialization"""
        self.logger.info("Starting plugin")
        self.publish(Event("plugin.started", {"name": self.name}))
    
    def handle_startup(self, event: Event):
        """Handle system startup"""
        self.logger.info("System starting")
    
    def stop(self):
        """Plugin cleanup"""
        self.logger.info("Stopping plugin")
```

3. Configure the plugin:
```toml
# plugin.toml
name = "my-plugin"
version = "0.1.0"
description = "My custom plugin"

[settings]
log_level = "info"

[dependencies]
required = []
optional = []
```

## Testing

Run the test suite:

```bash
# Run all tests with coverage
pytest tests/ -v --cov=core --cov=cli

# Run specific test categories
pytest tests/core/ -v  # Core tests
pytest tests/cli/ -v   # CLI tests

# Generate coverage reports
coverage html  # HTML report
coverage xml   # XML report
```

## Development

1. Install development dependencies:
```bash
pip install -e .[dev]
```

2. Run linters:
```bash
black .
isort .
mypy .
```

3. Run tests:
```bash
pytest tests/ -v
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linters
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.