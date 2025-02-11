#!/usr/bin/env python3
"""
Test script for MetaRepos cookiecutter template.
This script:
1. Creates a test output directory
2. Generates a test project from the template
3. Sets up the environment
4. Creates a test plugin
5. Runs the tests
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON_VERSION = (3, 11)

def check_requirements():
    """Check if all requirements are met."""
    # Check Python version
    if sys.version_info[:2] < MIN_PYTHON_VERSION:
        print(f"Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher is required")
        sys.exit(1)
    
    # Check if cookiecutter is installed
    try:
        subprocess.run(
            ["cookiecutter", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: cookiecutter is not installed")
        print("Please install requirements: pip install -r requirements-test.txt")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: cookiecutter command not found")
        print("Please install requirements: pip install -r requirements-test.txt")
        sys.exit(1)

def run_command(cmd, cwd=None, env=None):
    """Run a command and check its return code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env or os.environ,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Error output:", result.stderr)
        print("Console output:", result.stdout)
        sys.exit(1)
    return result.stdout

def create_cookiecutter_config(output_dir: Path) -> Path:
    """Create a cookiecutter config file."""
    config = {
        "default_context": {
            "project_name": "test-monorepo",
            "project_description": "A test monorepo",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "version": "0.1.0",
            "python_version": "3.11"
        }
    }
    
    config_dir = output_dir / ".cookiecutter"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.yaml"
    
    with open(config_file, "w") as f:
        json.dump(config, f)
    
    return config_file

def setup_venv(meta_dir: Path) -> tuple[str, str]:
    """Set up virtual environment and return pip and python paths."""
    print("\nCreating virtual environment...")
    try:
        run_command(["python", "-m", "venv", ".venv"], cwd=meta_dir)
        
        venv_pip = str(meta_dir / ".venv" / "bin" / "pip")
        venv_python = str(meta_dir / ".venv" / "bin" / "python")
        
        # Verify virtual environment
        if not os.path.exists(venv_pip) or not os.path.exists(venv_python):
            raise RuntimeError("Virtual environment creation failed")
        
        return venv_pip, venv_python
    
    except Exception as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)

def main():
    # Check requirements first
    check_requirements()
    
    # Create test output directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    output_dir = script_dir / "test-output"
    
    # Clean up existing test output
    if output_dir.exists():
        print(f"Cleaning up existing test output: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create fresh test output directory
    output_dir.mkdir()
    print(f"Created test output directory: {output_dir}")
    
    try:
        # Create cookiecutter config
        config_file = create_cookiecutter_config(output_dir)
        
        # Generate project from template
        print("\nGenerating test project...")
        run_command([
            "cookiecutter",
            "--no-input",
            "--config-file",
            str(config_file),
            str(script_dir)
        ], cwd=output_dir)
        
        # The project_slug will be automatically generated from project_name
        project_dir = output_dir / "test-monorepo"
        meta_dir = project_dir / "meta"
        
        # Create Python package structure
        print("\nSetting up Python package structure...")
        (meta_dir / "cli").mkdir(exist_ok=True)
        (meta_dir / "core").mkdir(exist_ok=True)
        
        # Create __init__.py files
        (meta_dir / "cli" / "__init__.py").touch()
        (meta_dir / "core" / "__init__.py").touch()
        
        # Set up virtual environment
        venv_pip, venv_python = setup_venv(meta_dir)
        
        # Install build dependencies
        print("\nInstalling build dependencies...")
        run_command([venv_pip, "install", "hatchling"], cwd=meta_dir)
        
        # Install the package in editable mode with dev dependencies
        print("\nInstalling package in editable mode with dev dependencies...")
        run_command([venv_pip, "install", "-e", ".[dev]"], cwd=meta_dir)
        
        # Run core tests
        print("\nRunning core tests...")
        run_command([
            venv_python,
            "-m", "pytest",
            "tests/",
            "-v",
            "--cov=core"
        ], cwd=meta_dir)
        
        print("\nAll tests completed successfully!")
        print(f"\nTest output is available at: {output_dir}")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        sys.exit(1)
    finally:
        # Deactivate virtual environment if it exists
        if 'VIRTUAL_ENV' in os.environ:
            print("\nDeactivating virtual environment...")
            del os.environ['VIRTUAL_ENV']

if __name__ == "__main__":
    main()