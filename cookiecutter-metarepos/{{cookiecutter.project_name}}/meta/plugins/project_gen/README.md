# Project Generation Plugin

A MetaRepos plugin that generates projects from cookiecutter templates.

## Features

- 🎯 Template-based project generation
- 📦 Template management (add/remove)
- 🔧 Configurable hooks
- 🚀 Multiple template support
- 🧪 Comprehensive test suite

## Installation

1. Enable the plugin:
```bash
metarepos plugin enable project_gen
```

2. Install dependencies:
```bash
pip install cookiecutter>=2.5.0 GitPython>=3.1.40
```

## Configuration

Configure the plugin in `plugin.toml`:

```toml
# Directory for storing templates
template_dir = "templates"

# Template configurations
[templates.python_package]
name = "python_package"
description = "Basic Python package template"
version = "0.1.0"
url = "https://github.com/audreyfeldroy/cookiecutter-pypackage"

# Post-generation hooks
[hooks]
shell = [
    "git init",
    "pip install -e .[dev]"
]
python = [
    "hooks.setup:configure_environment",
    "hooks.git:initialize_repo"
]
```

## Events

The plugin emits the following events:

### Project Events

- `plugin:project_gen:generated`
  ```python
  {
      "template": str,      # Template name
      "output_path": str,   # Generated project path
      "context": dict       # Generation context
  }
  ```

### Template Events

- `plugin:project_gen:template_added`
  ```python
  {
      "template_path": str  # Path to added template
  }
  ```

- `plugin:project_gen:template_removed`
  ```python
  {
      "template_name": str  # Name of removed template
  }
  ```

### Monitor Events

- `plugin:project_gen:project_gen:started`
  ```python
  {
      "templates": List[str],  # Available templates
      "template_dir": str      # Template directory
  }
  ```

- `plugin:project_gen:project_gen:stopped`
  ```python
  {}  # No payload
  ```

### Error Events

- `plugin:project_gen:error`
  ```python
  {
      "error": str,           # Error message
      "template": str,        # Template name (optional)
      "template_path": str,   # Template path (optional)
      "context": dict        # Generation context (optional)
  }
  ```

## Usage Example

```python
from core.events import Event

def handle_project_generated(event: Event):
    template = event.payload["template"]
    output_path = event.payload["output_path"]
    print(f"Generated project from {template} at {output_path}")

# Subscribe to events
event_manager.subscribe("plugin:project_gen:generated", handle_project_generated)

# Generate a project
plugin.generate_project(
    "python_package",
    "projects/",
    {
        "project_name": "my-package",
        "version": "0.1.0",
        "description": "My Python package"
    }
)
```

## Template Structure

Templates should follow this structure:

```
template_name/
├── template.toml         # Template configuration
├── cookiecutter.json    # Template variables
├── hooks/              # Python hooks (optional)
│   └── setup.py
└── {{cookiecutter.project_name}}/  # Template content
    ├── README.md
    └── ...
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

- Template management tests
- Project generation tests
- Hook execution tests
- Event emission tests
- Error handling tests

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