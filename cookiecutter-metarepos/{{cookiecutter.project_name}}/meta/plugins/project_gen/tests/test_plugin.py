"""
Tests for the project generation plugin.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List

import pytest
import toml

from core.events import Event
from plugins.project_gen.plugin import ProjectGenPlugin

@pytest.fixture
def test_dir(tmp_path: Path) -> Path:
    """Provide a test directory."""
    return tmp_path / "test_repo"

@pytest.fixture
def template_dir(test_dir: Path) -> Path:
    """Provide a template directory."""
    template_dir = test_dir / "templates"
    template_dir.mkdir(parents=True)
    return template_dir

@pytest.fixture
def plugin(test_dir: Path, template_dir: Path) -> ProjectGenPlugin:
    """Provide a configured plugin instance."""
    plugin = ProjectGenPlugin()
    
    # Create test directory
    test_dir.mkdir(exist_ok=True)
    os.chdir(test_dir)
    
    # Create plugin config
    config = {
        "template_dir": str(template_dir),
        "templates": {
            "test_template": {
                "name": "test_template",
                "description": "Test template",
                "version": "0.1.0"
            }
        }
    }
    
    with open("plugin.toml", "w") as f:
        toml.dump(config, f)
    
    yield plugin
    
    # Cleanup
    plugin.stop()
    os.chdir("..")

@pytest.fixture
def test_template(template_dir: Path) -> Path:
    """Create a test template."""
    template_path = template_dir / "test_template"
    template_path.mkdir()
    
    # Create template.toml
    config = {
        "name": "test_template",
        "description": "Test template",
        "version": "0.1.0",
        "hooks": {
            "shell": ["echo 'test'"],
            "python": ["hooks.test:run"]
        }
    }
    
    with open(template_path / "template.toml", "w") as f:
        toml.dump(config, f)
    
    # Create cookiecutter.json
    with open(template_path / "cookiecutter.json", "w") as f:
        f.write('{"project_name": "test"}')
    
    # Create template content
    template_content = template_path / "{{cookiecutter.project_name}}"
    template_content.mkdir()
    (template_content / "README.md").write_text("# {{cookiecutter.project_name}}")
    
    return template_path

@pytest.fixture
def received_events() -> List[Event]:
    """Track received events."""
    events = []
    return events

def test_plugin_initialization(plugin: ProjectGenPlugin):
    """Test plugin initialization."""
    assert plugin.templates == {}
    assert plugin.template_dir is None

def test_plugin_start_stop(plugin: ProjectGenPlugin, test_template: Path):
    """Test plugin start and stop."""
    # Start plugin
    plugin.start()
    assert plugin.template_dir is not None
    assert "test_template" in plugin.templates
    
    # Stop plugin
    plugin.stop()
    assert plugin.templates == {}
    assert plugin.template_dir is None

def test_list_templates(plugin: ProjectGenPlugin, test_template: Path):
    """Test listing templates."""
    plugin.start()
    templates = plugin.list_templates()
    
    assert len(templates) == 1
    template = templates[0]
    assert template["name"] == "test_template"
    assert template["description"] == "Test template"
    assert template["version"] == "0.1.0"

def test_generate_project(
    plugin: ProjectGenPlugin,
    test_template: Path,
    test_dir: Path,
    received_events: List[Event]
):
    """Test project generation."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:project_gen:generated", event_callback)
    
    # Start plugin
    plugin.start()
    
    # Generate project
    output_dir = test_dir / "output"
    output_dir.mkdir()
    
    result = plugin.generate_project(
        "test_template",
        str(output_dir),
        {"project_name": "my_project"}
    )
    
    # Verify project was generated
    assert result is not None
    project_dir = Path(result)
    assert project_dir.exists()
    assert (project_dir / "README.md").exists()
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:project_gen:generated"
    assert event.payload["template"] == "test_template"
    assert event.payload["output_path"] == str(project_dir)

def test_generate_project_invalid_template(
    plugin: ProjectGenPlugin,
    test_dir: Path,
    received_events: List[Event]
):
    """Test generating project with invalid template."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:project_gen:error", event_callback)
    
    # Start plugin
    plugin.start()
    
    # Try to generate project
    output_dir = test_dir / "output"
    output_dir.mkdir()
    
    result = plugin.generate_project(
        "nonexistent",
        str(output_dir),
        {"project_name": "my_project"}
    )
    
    # Verify failure
    assert result is None
    
    # Verify error event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:project_gen:error"
    assert "Template not found" in event.payload["error"]

def test_add_template(
    plugin: ProjectGenPlugin,
    test_dir: Path,
    received_events: List[Event]
):
    """Test adding a template."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:project_gen:template_added", event_callback)
    
    # Start plugin
    plugin.start()
    
    # Create test template
    template_path = test_dir / "new_template"
    template_path.mkdir()
    (template_path / "template.toml").write_text("""
        name = "new_template"
        description = "New template"
        version = "0.1.0"
    """)
    
    # Add template
    success = plugin.add_template(str(template_path))
    assert success
    assert "new_template" in plugin.templates
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:project_gen:template_added"
    assert event.payload["template_path"] == str(template_path)

def test_remove_template(
    plugin: ProjectGenPlugin,
    test_template: Path,
    received_events: List[Event]
):
    """Test removing a template."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:project_gen:template_removed", event_callback)
    
    # Start plugin
    plugin.start()
    
    # Remove template
    success = plugin.remove_template("test_template")
    assert success
    assert "test_template" not in plugin.templates
    assert not test_template.exists()
    
    # Verify event
    assert len(received_events) == 1
    event = received_events[0]
    assert event.namespace == "plugin:project_gen:template_removed"
    assert event.payload["template_name"] == "test_template"

def test_hooks_execution(
    plugin: ProjectGenPlugin,
    test_template: Path,
    test_dir: Path
):
    """Test hook execution."""
    # Create hooks directory
    hooks_dir = test_dir / "output" / "my_project" / ".hooks"
    hooks_dir.mkdir(parents=True)
    
    # Create test hook
    hook_code = """
def run(output_path, context):
    with open(output_path + '/hook_ran', 'w') as f:
        f.write('success')
"""
    (hooks_dir / "test.py").write_text(hook_code)
    
    # Start plugin
    plugin.start()
    
    # Generate project
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    result = plugin.generate_project(
        "test_template",
        str(output_dir),
        {"project_name": "my_project"}
    )
    
    # Verify hook ran
    assert result is not None
    assert (Path(result) / "hook_ran").exists()

def test_monitor_start_stop_events(plugin: ProjectGenPlugin, received_events: List[Event]):
    """Test monitor start/stop events."""
    # Set up event tracking
    def event_callback(event: Event):
        received_events.append(event)
    plugin.event_manager.subscribe("plugin:project_gen:project_gen:started", event_callback)
    plugin.event_manager.subscribe("plugin:project_gen:project_gen:stopped", event_callback)
    
    # Start and stop plugin
    plugin.start()
    plugin.stop()
    
    # Verify events
    assert len(received_events) == 2
    assert received_events[0].namespace == "plugin:project_gen:project_gen:started"
    assert received_events[1].namespace == "plugin:project_gen:project_gen:stopped"