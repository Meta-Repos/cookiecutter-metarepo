# MetaRepos

## Overview
MetaRepos is designed to help users start, build, and maintain monorepos for their projects. The core philosophy is that managing monorepos involves more than just filesystem management - it requires a flexible, event-driven architecture that can adapt to different project needs through plugins.

## Architecture

### Core Components

1. Event Management System
   - Central process managing event distribution
   - ZeroMQ-based pub/sub system for efficient event handling
   - Namespaced events (e.g., `core:file:created`, `plugin:plugin_name:event_name`)
   - Event metadata as optional JSON payload
   - Central log file for event history and debugging

2. CLI Interface
   - Separate package for command-line interactions
   - Basic Commands:
     - `metarepo health`: Test that the system is working correctly
     - `metarepo status`: Show the status of the monorepo
     - `metarepo plugin list`: View installed plugins
     - `metarepo plugin install/uninstall`: Manage plugin installation
     - `metarepo plugin enable/disable`: Control plugin state

### Plugin System
MetaRepos is designed to be highly extensible through plugins.  Plugins can have long-running processes (called services) that can subscribe to and emit events. They can also just expose commands in the CLI (i.e. `metarepos <plugin_name> <command>`). Some plugins may present a virtual filesystem.

#### Plugin Structure
Each plugin consists of:
- Metadata file (version, author)
- Optional long-running service
- Python module for CLI integration
- Configuration file (plugin.toml)

#### Plugin Providers
- Initial provider is the core MetaRepos repository
- Plugins are organized as folders within provider repositories
- Version management through git repository updates

#### Core Plugins
Provided in the base package with 'core-' prefix:

1. Core File System Monitor
   - Watch for file system events (create, modify, delete)
   - Generate namespaced events (e.g., `core:file:created`)
   - Provide basic filesystem monitoring capabilities

#### Additional Plugins

1. AI Integration Plugin
   - MCP (Model Context Protocol) server implementation
   - Expose monorepo information to AI chatbots
   - Maintain project documentation and memory bank

2. Data-Centric Development Plugin
   - Version control for data models
   - Auto-generate libraries from data models
   - Maintain consistency between data models and code

3. Project Generation Plugin
   - Custom cookiecutter templates for subprojects
   - Code generation from OpenAPI specs (e.g., using Connexion)
   - GitHub/GitLab integration for repository management

## Configuration
metarepo.toml structure:
```toml
[core]
# Core configuration settings

[plugins]
# Plugin-specific configurations

[plugins.plugin-name]
# Individual plugin settings
```

## Project Structure
Initial tree structure for a new monorepo:

```
meta/                   # Built-in folder of metarepo + supporting software
    .venv/              # Virtual env
    pyproject.toml      # Setup for virtualenv
    uv.lock             # Uv packages for python dependencies
    cli/                # CLI package
    core/               # Core event management system
    plugins/            # Plugin management and core plugins
    metarepo.toml       # Global config file (submodules can have metarepo.toml)
src/                    # Project contents
    data_model/         # Data model files (RDF stack preferred)
    libraries/          # Shared libraries across projects
    projects/           # Subprojects (APIs, frontends, etc.)
    docs/               # A plugin can present a virtual filesystem (in this example, mounting all doc/ folders from projects into a single place)
```

## Setup
MetaRepos uses cookiecutter to create new monorepo projects, featuring:
- Modern Python packaging with uv
- Virtual environment management
- Plugin-based architecture for extensibility
- Event-driven system for real-time monitoring and actions

The goal is to ensure consistency in how developers work with the codebase, eliminating the need for extensive setup instructions - just checkout the repo and start working. The event-driven architecture ensures that plugins can react to changes in real-time, providing a dynamic and responsive development environment.