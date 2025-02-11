# {{ cookiecutter.plugin_name }}

{{ cookiecutter.plugin_description }}

## Features

{% if cookiecutter.has_service == 'y' -%}
- Long-running service that handles events
{% endif -%}
{% if cookiecutter.has_cli == 'y' -%}
- CLI commands for plugin management
{% endif -%}
{% if cookiecutter.has_filesystem == 'y' -%}
- Virtual filesystem integration
{% endif %}

## Installation

1. Install the plugin using MetaRepos:
   ```bash
   metarepo plugin install {{ cookiecutter.plugin_slug }}
   ```

2. Enable the plugin:
   ```bash
   metarepo plugin enable {{ cookiecutter.plugin_slug }}
   ```

## Configuration

The plugin can be configured in your `metarepo.toml`:

```toml
[plugins.{{ cookiecutter.plugin_slug }}]
# Add your configuration options here
# example_option = "value"
```

{% if cookiecutter.has_cli == 'y' -%}
## CLI Commands

Check plugin status:
```bash
metarepo {{ cookiecutter.plugin_slug }} status
```
{% endif %}

## Events

The plugin emits and listens for the following events:

{% if cookiecutter.has_service == 'y' -%}
### Emitted Events
- `plugin:{{ cookiecutter.plugin_slug }}:started`: Emitted when the service starts
- `plugin:{{ cookiecutter.plugin_slug }}:stopped`: Emitted when the service stops

### Handled Events
- `core:system:shutdown`: Handles graceful shutdown of the service
{% endif %}

## Development

1. Clone the plugin repository
2. Make your changes
3. Test the plugin:
   ```bash
   # Run plugin tests
   pytest tests/
   ```

## Author

{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>