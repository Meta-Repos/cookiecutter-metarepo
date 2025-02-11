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
- cookiecutter

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

[events]
# Event system configuration
host = "127.0.0.1"
port = 5555
protocol = "tcp"

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

## Testing

The template includes a test script that validates both the template and generated projects:

```bash
# Make the test script executable
chmod +x test_template.py

# Run the tests
./test_template.py
```

The test script:
1. Creates a temporary test project from the template
2. Sets up the Python environment
3. Creates a test plugin using the plugin template
4. Runs the core system tests
5. Runs the plugin tests

This ensures that:
- The template generates valid projects
- The core system works correctly
- The plugin system functions as expected
- Configuration validation works properly

## License

MIT