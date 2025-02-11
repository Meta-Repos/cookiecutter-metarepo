"""
Post-generation script for MetaRepos cookiecutter template.
"""
import os
import subprocess
from pathlib import Path

def main():
    """Initialize the project after generation."""
    project_dir = Path.cwd()
    meta_dir = project_dir / "meta"
    
    print("Initializing MetaRepos project...")
    
    # Create virtual environment using uv
    print("Creating virtual environment...")
    try:
        subprocess.run(
            ["uv", "venv", ".venv"],
            cwd=meta_dir,
            check=True
        )
        
        # Install dependencies
        print("Installing dependencies...")
        subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            cwd=meta_dir,
            check=True
        )
        
        print("Installing development dependencies...")
        subprocess.run(
            ["uv", "pip", "install", "-e", ".[dev]"],
            cwd=meta_dir,
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

# MetaRepos
logs/
*.log
""".strip())
        
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from MetaRepos template"],
            cwd=project_dir,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during git initialization: {e}")
        return
    
    print("\nMetaRepos project initialized successfully!")
    print("\nNext steps:")
    print("1. cd into your project directory")
    print("2. Activate the virtual environment:")
    print("   source meta/.venv/bin/activate")
    print("3. Run 'metarepo health' to verify the installation")

if __name__ == "__main__":
    main()