#!/usr/bin/env python3
"""
Setup script for LLM Edge AI project
Helps initialize the development environment
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(e.stderr)
        return False


def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required, but found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def check_docker():
    """Check if Docker is installed"""
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            capture_output=True
        )
        print("✅ Docker is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker.")
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creating .env file from .env.example")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created")
    elif env_file.exists():
        print("ℹ️  .env file already exists")
    else:
        print("⚠️  .env.example not found")


def main():
    """Main setup function"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║          LLM Edge AI - Development Setup                  ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Docker
    if not check_docker():
        print("\n⚠️  Docker is recommended but not required for basic development")
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        print("⚠️  Failed to upgrade pip, continuing anyway...")
    
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing project dependencies"
    ):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Install development dependencies
    response = input("\n❓ Install development dependencies? (pytest, black, etc.) [Y/n]: ")
    if response.lower() in ['', 'y', 'yes']:
        if run_command(
            f"{sys.executable} -m pip install -r requirements-dev.txt",
            "Installing development dependencies"
        ):
            print("✅ Development dependencies installed")
    
    # Create .env file
    create_env_file()
    
    # Run tests
    response = input("\n❓ Run tests to verify setup? [Y/n]: ")
    if response.lower() in ['', 'y', 'yes']:
        run_command(
            f"{sys.executable} -m pytest tests/ -v",
            "Running tests"
        )
    
    # Summary
    print("""
╔═══════════════════════════════════════════════════════════╗
║                   Setup Complete! 🎉                      ║
╚═══════════════════════════════════════════════════════════╝

Next steps:

1. Generate docker-compose.yml:
   python3 scripts/generate-compose.py --devices 10

2. Start the simulation:
   docker compose up --build

3. Monitor telemetry:
   python3 src/mqtt_consumer.py

4. Run tests:
   pytest

5. Format code:
   black src/ tests/

For more information, see README.md

Happy coding! 🚀
    """)


if __name__ == "__main__":
    main()
