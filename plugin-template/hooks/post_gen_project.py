"""
Post-generation script for MetaRepos plugin template.
"""
import os
import subprocess
from pathlib import Path

def main():
    """Initialize the plugin project after generation."""
    project_dir = Path.cwd()
    
    print(f"Initializing plugin: {{ cookiecutter.plugin_name }}")
    
    # Create virtual environment
    print("Creating virtual environment...")
    try:
        subprocess.run(
            ["python", "-m", "venv", ".venv"],
            cwd=project_dir,
            check=True
        )
        
        # Install dependencies
        print("Installing dependencies...")
        subprocess.run(
            [".venv/bin/pip", "install", "-e", ".[dev]"],
            cwd=project_dir,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during dependency installation: {e}")
        return
    
    # Initialize git repository
    print("Initializing git repository...")
    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=True)
        
        # Create initial .gitignore
        gitignore_path = project_dir / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
""".strip())
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from MetaRepos plugin template"],
            cwd=project_dir,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during git initialization: {e}")
        return
    
    print(f"\n{{ cookiecutter.plugin_name }} plugin initialized successfully!")
    print("\nNext steps:")
    print("1. cd into your plugin directory")
    print("2. Activate the virtual environment:")
    print("   source .venv/bin/activate")
    print("3. Run the tests:")
    print("   pytest")

if __name__ == "__main__":
    main()