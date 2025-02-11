"""
Tests for the MetaRepos CLI.
"""
import os
import re
from pathlib import Path
from typing import Dict, Callable

import pytest
import toml
from click.testing import CliRunner

from cli.main import cli, get_config_path, load_config, __version__

def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class TestConfigFunctions:
    """Tests for configuration-related functions."""
    
    def test_get_config_path_default(self):
        """Test getting default config path."""
        if "METAREPOS_CONFIG" in os.environ:
            del os.environ["METAREPOS_CONFIG"]
        
        path = get_config_path()
        assert path == Path("metarepo.toml")
    
    def test_get_config_path_env(self, tmp_path: Path):
        """Test getting config path from environment."""
        config_path = tmp_path / "test-config.toml"
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        path = get_config_path()
        assert path == config_path
    
    def test_load_config_missing(self):
        """Test loading missing config."""
        if "METAREPOS_CONFIG" in os.environ:
            del os.environ["METAREPOS_CONFIG"]
        
        config = load_config()
        assert config == {}
    
    def test_load_config_invalid(self, tmp_path: Path):
        """Test loading invalid config."""
        config_path = tmp_path / "invalid.toml"
        config_path.write_text("invalid toml content")
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        config = load_config()
        assert config == {}

class TestBasicCommands:
    """Tests for basic CLI commands."""
    
    def test_cli_help(self, isolated_cli_runner: CliRunner):
        """Test the CLI help command."""
        result = isolated_cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "MetaRepos - Monorepo Management Tool" in result.output
        assert "Commands:" in result.output
        assert "health" in result.output
        assert "status" in result.output
        assert "plugin" in result.output
    
    def test_cli_version(self, isolated_cli_runner: CliRunner):
        """Test the CLI version command."""
        result = isolated_cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert f"metarepos, version {__version__}" in result.output
    
    def test_health_command_no_config(self, isolated_cli_runner: CliRunner):
        """Test the health command with no config."""
        result = isolated_cli_runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "default configuration" in strip_ansi(result.output)
    
    def test_health_command_with_config(self, isolated_cli_runner: CliRunner, temp_dir: Path, test_config: Dict):
        """Test the health command with config."""
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(test_config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "MetaRepos is healthy" in strip_ansi(result.output)
    
    def test_status_command_no_dirs(self, isolated_cli_runner: CliRunner):
        """Test the status command with no directories."""
        result = isolated_cli_runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "Using defaults" in output
        assert "Not found" in output
    
    def test_status_command_with_dirs(self, isolated_cli_runner: CliRunner, temp_dir: Path, test_config: Dict):
        """Test the status command with directories."""
        # Create directories
        (temp_dir / "plugins").mkdir()
        (temp_dir / "logs").mkdir()
        
        # Create config
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(test_config, f)
        
        # Set environment
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        os.environ["METAREPOS_PLUGIN_DIR"] = str(temp_dir / "plugins")
        os.environ["METAREPOS_LOG_DIR"] = str(temp_dir / "logs")
        
        result = isolated_cli_runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "✓ Loaded" in output
        assert "✓ Found" in output

class TestPluginCommands:
    """Tests for plugin-related commands."""
    
    def test_plugin_help(self, isolated_cli_runner: CliRunner):
        """Test the plugin help command."""
        result = isolated_cli_runner.invoke(cli, ["plugin", "--help"])
        assert result.exit_code == 0
        assert "Manage MetaRepos plugins" in result.output
        assert "list" in result.output
        assert "install" in result.output
        assert "uninstall" in result.output
        assert "enable" in result.output
        assert "disable" in result.output
    
    def test_plugin_list_no_dir(self, isolated_cli_runner: CliRunner):
        """Test the plugin list command with no plugin directory."""
        result = isolated_cli_runner.invoke(cli, ["plugin", "list"])
        assert result.exit_code == 0
        assert "Plugin directory not found" in strip_ansi(result.output)
    
    def test_plugin_list_empty_dir(self, isolated_cli_runner: CliRunner, temp_dir: Path):
        """Test the plugin list command with empty plugin directory."""
        plugin_dir = temp_dir / "plugins"
        plugin_dir.mkdir()
        os.environ["METAREPOS_PLUGIN_DIR"] = str(plugin_dir)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "list"])
        assert result.exit_code == 0
        assert "Installed Plugins" in result.output
    
    def test_plugin_list_with_plugins(
        self,
        isolated_cli_runner: CliRunner,
        setup_test_plugin: Callable[[str], Path],
        temp_dir: Path,
        test_config: Dict
    ):
        """Test the plugin list command with installed plugins."""
        # Create test plugins
        plugin_dir = temp_dir / "plugins"
        plugin_dir.mkdir()
        os.environ["METAREPOS_PLUGIN_DIR"] = str(plugin_dir)
        
        setup_test_plugin("test-plugin-1")
        setup_test_plugin("test-plugin-2")
        
        # Create config with enabled plugin
        config = test_config.copy()
        config["plugins"] = {"enabled": ["test-plugin-1"]}
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "list"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "test-plugin-1" in output
        assert "test-plugin-2" in output
        assert "Enabled" in output
        assert "Disabled" in output
    
    def test_plugin_uninstall(
        self,
        isolated_cli_runner: CliRunner,
        setup_test_plugin: Callable[[str], Path]
    ):
        """Test the plugin uninstall command."""
        # Create test plugin
        plugin_path = setup_test_plugin("test-plugin")
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "uninstall", "test-plugin"])
        assert result.exit_code == 0
        assert "Successfully uninstalled" in strip_ansi(result.output)
        assert not plugin_path.exists()
    
    def test_plugin_uninstall_missing(self, isolated_cli_runner: CliRunner):
        """Test uninstalling a missing plugin."""
        result = isolated_cli_runner.invoke(cli, ["plugin", "uninstall", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in strip_ansi(result.output)
    
    def test_plugin_enable(
        self,
        isolated_cli_runner: CliRunner,
        setup_test_plugin: Callable[[str], Path],
        temp_dir: Path,
        test_config: Dict
    ):
        """Test the plugin enable command."""
        # Create test plugin
        setup_test_plugin("test-plugin")
        
        # Create config
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(test_config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "enable", "test-plugin"])
        assert result.exit_code == 0
        assert "Successfully enabled" in strip_ansi(result.output)
        
        # Verify config was updated
        with open(config_path) as f:
            config = toml.load(f)
            assert "test-plugin" in config["plugins"]["enabled"]
    
    def test_plugin_enable_missing(self, isolated_cli_runner: CliRunner, temp_dir: Path, test_config: Dict):
        """Test enabling a missing plugin."""
        # Create config
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(test_config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "enable", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in strip_ansi(result.output)
    
    def test_plugin_disable(
        self,
        isolated_cli_runner: CliRunner,
        setup_test_plugin: Callable[[str], Path],
        temp_dir: Path,
        test_config: Dict
    ):
        """Test the plugin disable command."""
        # Create test plugin
        setup_test_plugin("test-plugin")
        
        # Create config with enabled plugin
        config = test_config.copy()
        config["plugins"] = {"enabled": ["test-plugin"]}
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "disable", "test-plugin"])
        assert result.exit_code == 0
        assert "Successfully disabled" in strip_ansi(result.output)
        
        # Verify config was updated
        with open(config_path) as f:
            config = toml.load(f)
            assert "test-plugin" not in config["plugins"]["enabled"]
    
    def test_plugin_disable_not_enabled(
        self,
        isolated_cli_runner: CliRunner,
        temp_dir: Path,
        test_config: Dict
    ):
        """Test disabling a plugin that isn't enabled."""
        # Create config
        config_path = temp_dir / "metarepo.toml"
        with open(config_path, "w") as f:
            toml.dump(test_config, f)
        os.environ["METAREPOS_CONFIG"] = str(config_path)
        
        result = isolated_cli_runner.invoke(cli, ["plugin", "disable", "test-plugin"])
        assert result.exit_code == 0
        assert "not enabled" in strip_ansi(result.output)

def test_invalid_command(isolated_cli_runner: CliRunner):
    """Test invoking an invalid command."""
    result = isolated_cli_runner.invoke(cli, ["invalid-command"])
    assert result.exit_code != 0
    assert "No such command" in result.output

def test_missing_config(isolated_cli_runner: CliRunner):
    """Test CLI behavior with missing config."""
    if "METAREPOS_CONFIG" in os.environ:
        del os.environ["METAREPOS_CONFIG"]
    
    result = isolated_cli_runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "Using defaults" in strip_ansi(result.output)

def test_missing_plugin_dir(isolated_cli_runner: CliRunner):
    """Test CLI behavior with missing plugin directory."""
    if "METAREPOS_PLUGIN_DIR" in os.environ:
        del os.environ["METAREPOS_PLUGIN_DIR"]
    
    result = isolated_cli_runner.invoke(cli, ["plugin", "list"])
    assert result.exit_code == 0
    assert "Plugin directory not found" in strip_ansi(result.output)

def test_version_format():
    """Test version string format."""
    assert re.match(r'^\d+\.\d+\.\d+$', __version__), "Version should be in format X.Y.Z"