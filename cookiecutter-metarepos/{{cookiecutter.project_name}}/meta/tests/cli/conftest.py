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
    env = os.environ.copy()
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
def isolated_cli_runner(cli_env: Dict[str, str], setup_test_env) -> Generator[CliRunner, None, None]:
    """Provide an isolated CLI runner with test environment."""
    runner = CliRunner(env=cli_env)
    with runner.isolated_filesystem():
        yield runner

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