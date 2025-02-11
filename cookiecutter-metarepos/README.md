# MetaRepos Template

A cookiecutter template for creating monorepo management tools with MetaRepos.

## Features

- 🔧 **Plugin System**: Extensible plugin architecture for custom functionality
- 📦 **Event System**: Robust event management with ZMQ pub/sub
- 🛠️ **CLI Interface**: Rich command-line interface with plugin management
- 📝 **Configuration**: TOML-based configuration with environment variable support
- 🧪 **Test Coverage**: Comprehensive test suite with coverage reporting
- 📚 **Documentation**: Detailed documentation and examples

## Requirements

- Python 3.11+
- cookiecutter
- Git

## Installation

```bash
# Install cookiecutter
pip install cookiecutter

# Create a new project
cookiecutter gh:rooveterinaryinc/cookiecutter-metarepos
```

## Project Structure

```
mymonorepo/
├── meta/                 # MetaRepos management tool
│   ├── cli/             # CLI implementation
│   ├── core/            # Core functionality
│   │   ├── events/      # Event system
│   │   └── plugin/      # Plugin system
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

## Configuration

The tool is configured through `metarepo.toml` and environment variables:

```toml
[meta]
name = "mymonorepo"
version = "0.1.0"
description = "My monorepo management tool"

[plugins]
directory = "plugins"
enabled = []

[events]
host = "127.0.0.1"
port = 5555
protocol = "tcp"
```

Environment variables:
- `METAREPOS_CONFIG`: Path to configuration file
- `METAREPOS_PLUGIN_DIR`: Plugin directory location
- `METAREPOS_LOG_DIR`: Log directory location

## CLI Commands

```bash
# Show help
metarepos --help

# Check health status
metarepos health

# Show monorepo status
metarepos status

# Plugin management
metarepos plugin list
metarepos plugin install <plugin>
metarepos plugin uninstall <plugin>
metarepos plugin enable <plugin>
metarepos plugin disable <plugin>
```

## Plugin Development

Plugins extend the tool's functionality:

```python
from core.plugin import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__()
    
    def start(self):
        # Plugin initialization
        pass
    
    def stop(self):
        # Plugin cleanup
        pass
```

Configuration in `plugin.toml`:
```toml
name = "my-plugin"
version = "0.1.0"
description = "My custom plugin"
```

## Testing

The project includes comprehensive tests:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
python test_template.py
```

Test coverage reports are generated in HTML and XML formats.

## Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -e .[dev]
```

3. Run tests:
```bash
pytest tests/ -v --cov=core --cov=cli
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.