"""
Main CLI entry point for MetaRepos.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click
import toml
from rich.console import Console
from rich.table import Table

# Package version
__version__ = "0.1.0"

console = Console()

def get_config_path() -> Path:
    """Get the configuration file path."""
    if "METAREPOS_CONFIG" in os.environ:
        return Path(os.environ["METAREPOS_CONFIG"])
    return Path("metarepo.toml")

def load_config() -> dict:
    """Load the MetaRepos configuration."""
    config_path = get_config_path()
    if not config_path.exists() or not config_path.is_file():
        return {}
    
    try:
        with open(config_path) as f:
            return toml.load(f)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        return {}

def get_plugin_dir() -> Path:
    """Get the plugin directory path."""
    if "METAREPOS_PLUGIN_DIR" in os.environ:
        return Path(os.environ["METAREPOS_PLUGIN_DIR"])
    return Path("plugins")

def get_log_dir() -> Path:
    """Get the log directory path."""
    if "METAREPOS_LOG_DIR" in os.environ:
        return Path(os.environ["METAREPOS_LOG_DIR"])
    return Path("logs")

class MetaReposCLI(click.Group):
    """Custom CLI group that handles command errors."""
    
    def get_command(self, ctx, cmd_name):
        """Get a command by name."""
        cmd = super().get_command(ctx, cmd_name)
        if cmd is None:
            # Print to stderr and return None to trigger error handling
            click.echo("No such command", err=True)
            ctx.exit(2)
        return cmd

@click.group(cls=MetaReposCLI)
@click.version_option(version=__version__, prog_name="metarepos")
def cli() -> None:
    """MetaRepos - Monorepo Management Tool"""
    pass

@cli.command()
def health() -> None:
    """Check the health status of MetaRepos."""
    config_path = get_config_path()
    if not config_path.exists() or not config_path.is_file():
        console.print("[yellow]MetaRepos is running with default configuration[/yellow]")
    else:
        console.print("[green]MetaRepos is healthy[/green]")

@cli.command()
def status() -> None:
    """Show the current status of the monorepo."""
    config_path = get_config_path()
    
    table = Table(title="MetaRepos Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="yellow")
    
    # Configuration status
    if config_path.exists() and config_path.is_file():
        table.add_row("Configuration", "✓ Loaded")
    else:
        table.add_row("Configuration", "⚠ Using defaults")
    
    # Plugin directory status
    plugin_dir = get_plugin_dir()
    if plugin_dir.exists() and plugin_dir.is_dir():
        table.add_row("Plugin Directory", "✓ Found")
    else:
        table.add_row("Plugin Directory", "⚠ Not found")
    
    # Log directory status
    log_dir = get_log_dir()
    if log_dir.exists() and log_dir.is_dir():
        table.add_row("Log Directory", "✓ Found")
    else:
        table.add_row("Log Directory", "⚠ Not found")
    
    console.print(table)

@cli.group()
def plugin() -> None:
    """Manage MetaRepos plugins."""
    pass

@plugin.command(name="list")
def list_plugins() -> None:
    """List all installed plugins."""
    config = load_config()
    plugin_dir = get_plugin_dir()
    
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        console.print("[yellow]⚠ Plugin directory not found[/yellow]")
        return
    
    # Check if directory is empty or has no valid plugins
    has_plugins = False
    for plugin_path in plugin_dir.iterdir():
        if plugin_path.is_dir() and (plugin_path / "plugin.toml").exists():
            has_plugins = True
            break
    
    if not has_plugins:
        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        console.print(table)
        return
    
    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Status", style="yellow")
    
    enabled_plugins = config.get("plugins", {}).get("enabled", [])
    
    for plugin_path in plugin_dir.iterdir():
        if plugin_path.is_dir():
            plugin_toml = plugin_path / "plugin.toml"
            if plugin_toml.exists():
                try:
                    with open(plugin_toml) as f:
                        plugin_config = toml.load(f)
                    
                    name = plugin_config.get("name", plugin_path.name)
                    version = plugin_config.get("version", "unknown")
                    status = "Enabled" if name in enabled_plugins else "Disabled"
                    
                    table.add_row(name, version, status)
                except Exception as e:
                    console.print(f"[red]Error loading plugin {plugin_path.name}: {e}[/red]")
    
    console.print(table)

@plugin.command()
@click.argument("plugin_name")
def install(plugin_name: str) -> None:
    """Install a plugin."""
    console.print(f"[yellow]Installation of plugin '{plugin_name}' not yet implemented[/yellow]")

@plugin.command()
@click.argument("plugin_name")
def uninstall(plugin_name: str) -> None:
    """Uninstall a plugin."""
    plugin_dir = get_plugin_dir()
    plugin_path = plugin_dir / plugin_name
    
    if not plugin_path.exists():
        console.print(f"[yellow]Plugin '{plugin_name}' not found[/yellow]")
        return
    
    try:
        import shutil
        shutil.rmtree(plugin_path)
        console.print(f"[green]Successfully uninstalled plugin '{plugin_name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error uninstalling plugin '{plugin_name}': {e}[/red]")

@plugin.command()
@click.argument("plugin_name")
def enable(plugin_name: str) -> None:
    """Enable a plugin."""
    config = load_config()
    config_path = get_config_path()
    
    if not config:
        console.print("[red]No configuration file found[/red]")
        return
    
    plugin_dir = get_plugin_dir()
    plugin_path = plugin_dir / plugin_name
    
    if not plugin_path.exists():
        console.print(f"[yellow]Plugin '{plugin_name}' not found[/yellow]")
        return
    
    plugins = config.setdefault("plugins", {})
    enabled_plugins = plugins.setdefault("enabled", [])
    
    if plugin_name in enabled_plugins:
        console.print(f"[yellow]Plugin '{plugin_name}' is already enabled[/yellow]")
        return
    
    enabled_plugins.append(plugin_name)
    
    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
        console.print(f"[green]Successfully enabled plugin '{plugin_name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error enabling plugin '{plugin_name}': {e}[/red]")

@plugin.command()
@click.argument("plugin_name")
def disable(plugin_name: str) -> None:
    """Disable a plugin."""
    config = load_config()
    config_path = get_config_path()
    
    if not config:
        console.print("[red]No configuration file found[/red]")
        return
    
    plugins = config.get("plugins", {})
    enabled_plugins = plugins.get("enabled", [])
    
    if plugin_name not in enabled_plugins:
        console.print(f"[yellow]Plugin '{plugin_name}' is not enabled[/yellow]")
        return
    
    enabled_plugins.remove(plugin_name)
    
    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
        console.print(f"[green]Successfully disabled plugin '{plugin_name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error disabling plugin '{plugin_name}': {e}[/red]")

def main():
    """Main entry point."""
    try:
        cli()
    except click.exceptions.UsageError as e:
        click.echo(str(e), err=True)
        sys.exit(2)

if __name__ == "__main__":
    main()