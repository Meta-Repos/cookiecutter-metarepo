# MetaRepos Cookiecutter Template

This is a cookiecutter template for creating new monorepo projects managed by MetaRepos.

## Features

- Modern Python packaging with uv
- Event-driven plugin architecture
- Built-in monorepo management tools
- Extensible through plugins

## Requirements

- Python 3.11 or higher
- uv package manager
- git

## Usage

```bash
# Install cookiecutter if you haven't already
pip install cookiecutter

# Create a new project
cookiecutter gh:your-username/cookiecutter-metarepos

# Follow the prompts to configure your project
```

## Project Structure

```
meta/                   # Built-in folder of metarepo + supporting software
    .venv/              # Virtual env
    pyproject.toml      # Setup for virtualenv
    cli/                # CLI package
    core/               # Core event management system
    plugins/            # Plugin management and core plugins
    metarepo.toml       # Global config file
src/                    # Project contents
    data_model/         # Data model files
    libraries/          # Shared libraries across projects
    projects/           # Subprojects (APIs, frontends, etc.)
    docs/               # Documentation
```

## Configuration

The project is configured through `meta/metarepo.toml`:

```toml
[core]
# Core MetaRepos configuration
log_level = "info"
event_log_path = "logs/events.log"

[plugins]
# Plugin-specific configurations
enabled = []
search_paths = ["plugins"]
```

## Development

After creating your project:

1. Change into your project directory
2. Activate the virtual environment:
   ```bash
   source meta/.venv/bin/activate
   ```
3. Run the health check:
   ```bash
   metarepo health
   ```

## License

MIT