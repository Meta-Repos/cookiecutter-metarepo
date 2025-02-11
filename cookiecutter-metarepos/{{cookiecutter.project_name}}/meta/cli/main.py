"""
Main CLI entry point for MetaRepos.
"""
import os
from pathlib import Path
from typing import Optional

import click
import toml
from rich.console import Console
from rich.table import Table

console = Console()

def get_config_path() -> Path:
    """Get the configuration file path."""
    config_path = os.environ.get("METAREPOS_CONFIG", "metarepo.toml")
    return Path(config_path)

def load_config() -> dict:
    """Load the MetaRepos configuration."""
    config_path = get_config_path()
    if not config_path.exists():
        console.print("[yellow]Warning: Configuration file not found[/yellow]")
        return {}
    
    try:
        with open(config_path) as f:
            return toml.load(f)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        return {}

@click.group()
@click.version_option()
def cli() -> None:
    """MetaRepos - Monorepo Management Tool"""
    pass

@cli.command()
def health() -> None:
    """Check the health status of MetaRepos."""
    config = load_config()
    
    if not config:
        console.print("[yellow]MetaRepos is running with default configuration[/yellow]")
    else:
        console.print("[green]MetaRepos is healthy[/green]")

@cli.command()
def status() -> None:
    """Show the current status of the monorepo."""
    config = load_config()
    
    table = Table(title="MetaRepos Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    # Configuration status
    if config:
        table.add_row("Configuration", "✓ Loaded")
    else:
        table.add_row("Configuration", "⚠ Using defaults")
    
    # Plugin directory status
    plugin_dir = os.environ.get("METAREPOS_PLUGIN_DIR", "plugins")
    if Path(plugin_dir).exists():
        table.add_row("Plugin Directory", "✓ Found")
    else:
        table.add_row("Plugin Directory", "⚠ Not found")
    
    # Log directory status
    log_dir = os.environ.get("METAREPOS_LOG_DIR", "logs")
    if Path(log_dir).exists():
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
    plugin_dir = Path(os.environ.get("METAREPOS_PLUGIN_DIR", "plugins"))
    
    if not plugin_dir.exists():
        console.print("[yellow]Plugin directory not found[/yellow]")
        return
    
    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Status", style="yellow")
    
    enabled_plugins = config.get("plugins", {}).get("enabled", [])
    
    for plugin_path in plugin_dir.iterdir():
        if not plugin_path.is_dir():
            continue
        
        plugin_toml = plugin_path / "plugin.toml"
        if not plugin_toml.exists():
            continue
        
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
    plugin_dir = Path(os.environ.get("METAREPOS_PLUGIN_DIR", "plugins"))
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
    
    plugin_dir = Path(os.environ.get("METAREPOS_PLUGIN_DIR", "plugins"))
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

if __name__ == "__main__":
    cli()