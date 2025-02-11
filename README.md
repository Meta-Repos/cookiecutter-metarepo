# MetaRepos

A comprehensive monorepo management system with plugin architecture and event-driven design.

## Overview

MetaRepos provides a robust foundation for managing monorepos through:

- 🔌 **Plugin System**: Extensible architecture for custom functionality
- 📡 **Event System**: ZMQ-based pub/sub for real-time communication
- 🛠️ **CLI Tools**: Rich command-line interface for repo management
- 📦 **Templates**: Cookiecutter templates for quick setup
- 🧪 **Testing**: Comprehensive test suites with coverage reporting
- 📚 **Documentation**: Detailed guides and examples

## Repository Structure

```
MetaRepos/
├── cookiecutter-metarepos/   # Project template
│   ├── {{cookiecutter.project_name}}/
│   │   ├── meta/            # Management tool
│   │   │   ├── cli/        # CLI implementation
│   │   │   ├── core/       # Core functionality
│   │   │   └── tests/      # Test suite
│   │   └── src/            # Monorepo source
│   └── test_template.py     # Template tests
├── plugin-template/         # Plugin template
│   └── {{cookiecutter.plugin_slug}}/
│       ├── plugin.py       # Plugin implementation
│       └── tests/          # Plugin tests
└── memory-bank/            # Development tracking
    ├── activeContext.md    # Current context
    ├── productContext.md   # Project overview
    └── progress.md         # Development progress
```

## Components

### Project Template

The `cookiecutter-metarepos` template creates new monorepo projects with:

- Event-driven architecture for real-time updates
- Plugin system for extensibility
- CLI tools for repo management
- Comprehensive test suite
- Development tooling

### Plugin Template

The `plugin-template` creates new plugins with:

- Standard plugin interface
- Event system integration
- Configuration management
- Test infrastructure
- Documentation templates

### Memory Bank

The `memory-bank` tracks development with:

- Active development context
- Project requirements
- Implementation decisions
- Progress tracking
- Future planning

## Getting Started

1. Create a new monorepo:
```bash
cookiecutter gh:rooveterinaryinc/cookiecutter-metarepos
```

2. Create a new plugin:
```bash
cd mymonorepo/meta
cookiecutter gh:rooveterinaryinc/plugin-template
```

3. Install dependencies:
```bash
cd meta
pip install -e .[dev]
```

4. Run tests:
```bash
python test_template.py
```

## Development

- Python 3.11+
- ZeroMQ for event system
- Click for CLI
- PyTest for testing
- Coverage.py for reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
