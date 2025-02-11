# File System Monitor Plugin

A MetaRepos plugin that monitors file system changes in the monorepo and emits corresponding events.

## Features

- 👀 Real-time file system monitoring
- 🎯 Configurable watch paths
- 🚫 Customizable ignore patterns
- 📡 Event-driven architecture
- 🧪 Comprehensive test suite

## Installation

1. Enable the plugin:
```bash
metarepos plugin enable fs_monitor
```

2. Install dependencies:
```bash
pip install watchdog>=2.1.0
```

## Configuration

Configure the plugin in `plugin.toml`:

```toml
# Paths to monitor (relative to monorepo root)
watch_paths = [
    ".",           # Monitor entire monorepo
    "src/",        # Monitor source code
    "meta/plugins" # Monitor plugins
]

# Patterns to ignore
ignore_patterns = [
    ".git",
    "__pycache__",
    "*.pyc",
    ".coverage",
    # ... more patterns
]
```

## Events

The plugin emits the following events:

### File Events

- `plugin:fs_monitor:fs:created`
  ```python
  {
      "path": str,        # Path to created file/directory
      "is_directory": bool # True if directory, False if file
  }
  ```

- `plugin:fs_monitor:fs:deleted`
  ```python
  {
      "path": str,        # Path to deleted file/directory
      "is_directory": bool # True if directory, False if file
  }
  ```

- `plugin:fs_monitor:fs:modified`
  ```python
  {
      "path": str,        # Path to modified file/directory
      "is_directory": bool # True if directory, False if file
  }
  ```

- `plugin:fs_monitor:fs:moved`
  ```python
  {
      "src_path": str,     # Original path
      "dest_path": str,    # New path
      "is_directory": bool # True if directory, False if file
  }
  ```

### Monitor Events

- `plugin:fs_monitor:fs:monitor:started`
  ```python
  {
      "watch_paths": List[str],     # Active watch paths
      "ignore_patterns": List[str]  # Active ignore patterns
  }
  ```

- `plugin:fs_monitor:fs:monitor:stopped`
  ```python
  {}  # No payload
  ```

## Usage Example

```python
from core.events import Event

def handle_file_created(event: Event):
    path = event.payload["path"]
    is_dir = event.payload["is_directory"]
    print(f"{'Directory' if is_dir else 'File'} created: {path}")

# Subscribe to events
event_manager.subscribe("plugin:fs_monitor:fs:created", handle_file_created)
```

## Development

1. Install development dependencies:
```bash
pip install -e .[dev]
```

2. Run tests:
```bash
pytest tests/ -v
```

## Testing

The plugin includes comprehensive tests:

- Event emission tests
- File operation tests
- Directory operation tests
- Ignore pattern tests
- Monitor lifecycle tests

Run the tests with:
```bash
pytest tests/test_plugin.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This plugin is part of MetaRepos and is licensed under the MIT License.