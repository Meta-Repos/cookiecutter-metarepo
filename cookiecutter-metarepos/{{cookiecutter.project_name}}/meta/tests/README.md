# MetaRepos Test Suite

This directory contains the test suite for MetaRepos. The tests are organized by component and use pytest as the test framework.

## Test Structure

```
tests/
├── conftest.py           # Global test fixtures and configuration
├── core/                 # Core system tests
│   ├── events/          # Event system tests
│   │   ├── test_logger.py
│   │   ├── test_manager.py
│   │   └── test_schema.py
│   └── plugin/          # Plugin system tests
│       └── test_schema.py
└── cli/                 # CLI tests
    ├── conftest.py      # CLI-specific fixtures
    ├── test_config.toml # Test configuration
    └── test_main.py     # CLI command tests
```

## Test Categories

### Core Tests

- **Event System Tests**: Test the event logging, management, and schema validation
  - Event logging with rotation and cleanup
  - Event subscription and publishing
  - Event schema validation
  - Event manager lifecycle

- **Plugin System Tests**: Test the plugin loading and management
  - Plugin schema validation
  - Plugin loading and initialization
  - Plugin lifecycle management

### CLI Tests

- **Command Tests**: Test all CLI commands and their options
  - Basic commands (health, status)
  - Plugin management commands
  - Configuration handling
  - Error cases

- **Environment Tests**: Test environment variable handling
  - Configuration file location
  - Plugin directory location
  - Log directory location

## Test Fixtures

### Global Fixtures

- `test_config`: Provides test configuration
- `temp_dir`: Provides temporary directory for tests
- `setup_test_env`: Sets up test environment

### CLI Fixtures

- `cli_env`: Provides CLI environment variables
- `isolated_cli_runner`: Provides isolated CLI test environment
- `setup_test_plugin`: Creates test plugins

## Coverage Requirements

- Minimum 80% overall code coverage
- Branch coverage tracking enabled
- Missing line reporting
- Separate coverage for core and CLI
- Combined coverage reporting

## Running Tests

### Running All Tests

```bash
pytest tests/ -v --cov=core --cov=cli
```

### Running Specific Test Categories

```bash
# Run core tests only
pytest tests/core/ -v --cov=core

# Run CLI tests only
pytest tests/cli/ -v --cov=cli

# Run event system tests
pytest tests/core/events/ -v

# Run plugin system tests
pytest tests/core/plugin/ -v
```

### Coverage Report

```bash
# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## Test Guidelines

1. **Isolation**: Each test should be independent and not rely on state from other tests

2. **Fixtures**: Use fixtures for common setup and teardown

3. **Mocking**: Use mocking for external dependencies and time-based operations

4. **Coverage**: Ensure new code is covered by tests

5. **Documentation**: Document test purpose and any complex test scenarios

6. **Error Cases**: Include tests for error conditions and edge cases

7. **Configuration**: Use test configuration files for complex test scenarios

8. **Environment**: Clean up test environment after each test

## Adding New Tests

1. Create test file in appropriate directory
2. Add necessary fixtures to conftest.py
3. Follow existing test patterns
4. Include both success and error cases
5. Add to coverage configuration if needed
6. Document complex test scenarios
7. Verify coverage meets requirements

## Test Dependencies

Required packages for testing (included in [dev] extras):
- pytest
- pytest-cov
- pytest-asyncio
- freezegun
- coverage

## Continuous Integration

Tests are run automatically on:
- Pull requests
- Main branch commits
- Release tags

Coverage reports are generated and tracked for each run.