#!/usr/bin/env python3
"""Script to publish msd-sdk to PyPI.

Usage:
    python publish.py           # Publish current version
    python publish.py --bump    # Bump patch version and publish
    python publish.py --bump minor  # Bump minor version and publish
    python publish.py --bump major  # Bump major version and publish
"""

import subprocess
import sys
import os
import re
from getpass import getpass
from pathlib import Path


def get_current_version():
    """Read current version from pyproject.toml."""
    pyproject = Path(__file__).parent / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def bump_version(current: str, bump_type: str = "patch") -> str:
    """Bump version number."""
    parts = [int(p) for p in current.split(".")]
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")
    
    major, minor, patch = parts
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_version(new_version: str):
    """Update version in pyproject.toml and __init__.py."""
    root = Path(__file__).parent
    
    # Update pyproject.toml
    pyproject = root / "pyproject.toml"
    content = pyproject.read_text()
    content = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    pyproject.write_text(content)
    
    # Update __init__.py
    init_file = root / "src" / "msd_sdk" / "__init__.py"
    content = init_file.read_text()
    content = re.sub(
        r'^__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    init_file.write_text(content)


def clean_dist():
    """Remove old dist files."""
    dist_dir = Path(__file__).parent / "dist"
    if dist_dir.exists():
        for f in dist_dir.glob("*.whl"):
            f.unlink()
        for f in dist_dir.glob("*.tar.gz"):
            f.unlink()


def main():
    # Handle version bump
    bump_type = None
    if "--bump" in sys.argv:
        idx = sys.argv.index("--bump")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] in ("major", "minor", "patch"):
            bump_type = sys.argv[idx + 1]
        else:
            bump_type = "patch"
    
    current_version = get_current_version()
    
    if bump_type:
        new_version = bump_version(current_version, bump_type)
        print(f"Bumping version: {current_version} -> {new_version}")
        update_version(new_version)
        current_version = new_version
    
    print(f"Publishing msd-sdk v{current_version} to PyPI")
    print("-" * 40)
    
    # Get PyPI token
    token = getpass("Enter your PyPI API token (starts with pypi-): ")
    
    if not token.startswith("pypi-"):
        print("Error: Token should start with 'pypi-'")
        sys.exit(1)
    
    # Clean old dist files
    print("\nCleaning old dist files...")
    clean_dist()
    
    # Build
    print("Building package...")
    result = subprocess.run(["uv", "build"], cwd=Path(__file__).parent)
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    # Publish
    print("\nPublishing to PyPI...")
    env = os.environ.copy()
    env["UV_PUBLISH_TOKEN"] = token
    
    result = subprocess.run(
        ["uv", "publish"],
        cwd=Path(__file__).parent,
        env=env
    )
    
    if result.returncode == 0:
        print(f"\n✅ Successfully published msd-sdk v{current_version} to PyPI!")
        print("Install with: pip install msd-sdk")
        if bump_type:
            print(f"\nDon't forget to commit the version bump:")
            print(f"  git add -A && git commit -m 'Bump version to {current_version}'")
    else:
        print("\n❌ Publish failed. Check the error message above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
