"""
Test fixtures for CLI tests.
"""
import os
import tempfile
from pathlib import Path
from typing import Dict, Generator

import pytest
import toml
from click.testing import CliRunner

@pytest.fixture
def test_config() -> Dict:
    """Provide test configuration."""
    config_path = Path(__file__).parent / "test_config.toml"
    with open(config_path) as f:
        return toml.load(f)

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)

@pytest.fixture
def cli_env(temp_dir: Path) -> Dict[str, str]:
    """Provide environment variables for CLI tests."""
    env = {}  # Start with empty env instead of copying os.environ
    env["METAREPOS_CONFIG"] = str(temp_dir / "metarepo.toml")
    env["METAREPOS_PLUGIN_DIR"] = str(temp_dir / "plugins")
    env["METAREPOS_LOG_DIR"] = str(temp_dir / "logs")
    return env

@pytest.fixture
def test_plugin_template(test_config: Dict) -> str:
    """Provide the test plugin template."""
    return test_config["test"]["plugin_template"].strip()

@pytest.fixture
def test_plugin_toml(test_config: Dict) -> str:
    """Provide the test plugin.toml template."""
    return test_config["test"]["plugin_toml"].strip()

@pytest.fixture
def setup_test_env(temp_dir: Path, test_config: Dict, cli_env: Dict[str, str]) -> None:
    """Set up the test environment with configuration and directories."""
    # Create directories
    plugin_dir = Path(cli_env["METAREPOS_PLUGIN_DIR"])
    log_dir = Path(cli_env["METAREPOS_LOG_DIR"])
    plugin_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Write configuration
    config_path = Path(cli_env["METAREPOS_CONFIG"])
    with open(config_path, "w") as f:
        toml.dump(test_config, f)

@pytest.fixture
def isolated_cli_runner(cli_env: Dict[str, str], monkeypatch) -> Generator[CliRunner, None, None]:
    """Provide an isolated CLI runner with test environment."""
    # Clear environment variables
    for var in list(os.environ.keys()):
        monkeypatch.delenv(var, raising=False)
    
    # Set test environment variables
    for key, value in cli_env.items():
        monkeypatch.setenv(key, value)
    
    # Create runner with mix_stderr=True to capture stderr
    runner = CliRunner(mix_stderr=True)
    with runner.isolated_filesystem():
        # Change to the isolated directory
        cwd = os.getcwd()
        yield runner
        # Change back to original directory
        os.chdir(cwd)

@pytest.fixture
def setup_test_plugin(temp_dir: Path, test_plugin_template: str, test_plugin_toml: str):
    """Create a test plugin in the plugins directory."""
    def _setup_plugin(plugin_name: str) -> Path:
        plugin_dir = temp_dir / "plugins" / plugin_name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create plugin.py
        with open(plugin_dir / "plugin.py", "w") as f:
            f.write(test_plugin_template)
        
        # Create plugin.toml
        with open(plugin_dir / "plugin.toml", "w") as f:
            f.write(test_plugin_toml.format(plugin_name=plugin_name))
        
        return plugin_dir
    
    return _setup_plugin

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Clean environment variables before each test."""
    # Store original environment
    orig_env = dict(os.environ)
    
    # Clear environment variables
    for var in list(os.environ.keys()):
        monkeypatch.delenv(var, raising=False)
    
    yield
    
    # Restore original environment
    for var in list(os.environ.keys()):
        monkeypatch.delenv(var, raising=False)
    for key, value in orig_env.items():
        monkeypatch.setenv(key, value)