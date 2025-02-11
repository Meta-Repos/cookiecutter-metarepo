"""
Project generation plugin for MetaRepos.

This plugin provides project generation capabilities using cookiecutter templates.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import cookiecutter.main
from cookiecutter.exceptions import RepositoryNotFound

from core.events import Event
from core.plugin import Plugin

class ProjectGenPlugin(Plugin):
    """Plugin for generating projects from templates."""
    
    def __init__(self):
        super().__init__()
        self.templates: Dict[str, Dict] = {}
        self.template_dir: Optional[Path] = None
    
    def start(self):
        """Start the project generation plugin."""
        config = self.get_config()
        
        # Set up template directory
        self.template_dir = Path(config.get('template_dir', 'templates'))
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Load template configurations
        self.load_templates()
        
        # Emit startup event
        self.emit_event('project_gen:started', {
            'templates': list(self.templates.keys()),
            'template_dir': str(self.template_dir)
        })
    
    def stop(self):
        """Stop the project generation plugin."""
        self.templates.clear()
        self.template_dir = None
        self.emit_event('project_gen:stopped', {})
    
    def load_templates(self):
        """Load template configurations."""
        if not self.template_dir:
            return
        
        # Clear existing templates
        self.templates.clear()
        
        # Load each template configuration
        for template_dir in self.template_dir.iterdir():
            if not template_dir.is_dir():
                continue
            
            template_config = template_dir / "template.toml"
            if not template_config.exists():
                continue
            
            try:
                import toml
                config = toml.load(template_config)
                template_name = config.get('name')
                if template_name:
                    self.templates[template_name] = config
            except Exception as e:
                self.emit_event('project_gen:error', {
                    'error': f"Failed to load template {template_dir.name}: {e}"
                })
    
    def list_templates(self) -> List[Dict]:
        """List available templates."""
        return [
            {
                'name': name,
                'description': config.get('description', ''),
                'version': config.get('version', '0.1.0')
            }
            for name, config in self.templates.items()
        ]
    
    def generate_project(
        self,
        template_name: str,
        output_dir: str,
        context: Dict
    ) -> Optional[str]:
        """Generate a project from a template."""
        if template_name not in self.templates:
            self.emit_event('project_gen:error', {
                'error': f"Template not found: {template_name}"
            })
            return None
        
        template_config = self.templates[template_name]
        template_path = self.template_dir / template_name
        
        try:
            # Generate project
            output_path = cookiecutter.main.cookiecutter(
                str(template_path),
                no_input=True,
                output_dir=output_dir,
                extra_context=context
            )
            
            # Run post-generation hooks
            self._run_hooks(template_config, output_path, context)
            
            # Emit success event
            self.emit_event('project_gen:generated', {
                'template': template_name,
                'output_path': output_path,
                'context': context
            })
            
            return output_path
        
        except Exception as e:
            self.emit_event('project_gen:error', {
                'error': f"Failed to generate project: {e}",
                'template': template_name,
                'context': context
            })
            return None
    
    def _run_hooks(self, template_config: Dict, output_path: str, context: Dict):
        """Run post-generation hooks."""
        hooks = template_config.get('hooks', {})
        
        # Run shell commands
        for command in hooks.get('shell', []):
            try:
                subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    cwd=output_path
                )
            except subprocess.CalledProcessError as e:
                self.emit_event('project_gen:error', {
                    'error': f"Hook failed: {e}",
                    'command': command,
                    'output_path': output_path
                })
        
        # Run Python hooks
        python_hooks = hooks.get('python', [])
        if python_hooks:
            hooks_dir = Path(output_path) / '.hooks'
            if hooks_dir.exists() and hooks_dir.is_dir():
                import sys
                sys.path.insert(0, str(hooks_dir))
                
                for hook in python_hooks:
                    try:
                        module_name, func_name = hook.split(':')
                        module = __import__(module_name)
                        func = getattr(module, func_name)
                        func(output_path, context)
                    except Exception as e:
                        self.emit_event('project_gen:error', {
                            'error': f"Python hook failed: {e}",
                            'hook': hook,
                            'output_path': output_path
                        })
                
                sys.path.pop(0)
    
    def add_template(self, template_path: str) -> bool:
        """Add a template from a path or URL."""
        if not self.template_dir:
            return False
        
        try:
            # Clone or copy template
            if template_path.startswith(('http://', 'https://', 'git://')):
                import git
                repo = git.Repo.clone_from(
                    template_path,
                    self.template_dir / Path(template_path).stem
                )
                template_path = repo.working_dir
            else:
                template_path = Path(template_path)
                if template_path.is_dir():
                    shutil.copytree(
                        template_path,
                        self.template_dir / template_path.name
                    )
            
            # Reload templates
            self.load_templates()
            
            # Emit success event
            self.emit_event('project_gen:template_added', {
                'template_path': template_path
            })
            
            return True
        
        except Exception as e:
            self.emit_event('project_gen:error', {
                'error': f"Failed to add template: {e}",
                'template_path': template_path
            })
            return False
    
    def remove_template(self, template_name: str) -> bool:
        """Remove a template."""
        if not self.template_dir or template_name not in self.templates:
            return False
        
        try:
            # Remove template directory
            template_path = self.template_dir / template_name
            if template_path.exists():
                shutil.rmtree(template_path)
            
            # Remove from templates dict
            del self.templates[template_name]
            
            # Emit success event
            self.emit_event('project_gen:template_removed', {
                'template_name': template_name
            })
            
            return True
        
        except Exception as e:
            self.emit_event('project_gen:error', {
                'error': f"Failed to remove template: {e}",
                'template_name': template_name
            })
            return False
    
    def get_config(self) -> Dict:
        """Get plugin configuration."""
        try:
            with open('plugin.toml') as f:
                import toml
                return toml.load(f)
        except Exception:
            return {}
    
    def emit_event(self, namespace: str, payload: Dict):
        """Emit a project generation event."""
        event = Event.create(
            namespace=f'plugin:project_gen:{namespace}',
            payload=payload
        )
        self.event_manager.emit(event)