# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Project Structure

```
meta/                   # MetaRepos management and tools
    .venv/              # Virtual environment
    pyproject.toml      # Python package configuration
    cli/                # CLI package
    core/               # Core event management system
    plugins/            # Plugin management and core plugins
    metarepo.toml       # Global configuration file
src/                    # Project contents
    data_model/         # Data model files
    libraries/          # Shared libraries across projects
    projects/           # Subprojects (APIs, frontends, etc.)
    docs/               # Documentation
```

## Getting Started

1. Activate the virtual environment:
   ```bash
   source meta/.venv/bin/activate
   ```

2. Verify the installation:
   ```bash
   metarepo health
   ```

3. Check the status of your monorepo:
   ```bash
   metarepo status
   ```

## Plugin Management

List available plugins:
```bash
metarepo plugin list
```

Install a plugin:
```bash
metarepo plugin install <plugin-name>
```

Enable/disable plugins:
```bash
metarepo plugin enable <plugin-name>
metarepo plugin disable <plugin-name>
```

## Configuration

The monorepo is configured through `meta/metarepo.toml`. See the file for available options and documentation.

## Author

{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>