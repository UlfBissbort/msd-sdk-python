#!/usr/bin/env python3
"""
MSD SDK Publish Tool
====================

A friendly CLI tool for publishing the MSD SDK to PyPI.

INTERACTIVE MODE (default):
    python publish.py

    Shows a menu to select what you want to do:
    - Publish current version
    - Bump version and publish (patch/minor/major)

COMMAND LINE MODE:
    python publish.py publish              # Publish current version
    python publish.py publish --bump       # Bump patch version and publish
    python publish.py publish --bump minor # Bump minor version and publish
    python publish.py publish --bump major # Bump major version and publish
    python publish.py --help               # Show this help message
"""

import subprocess
import sys
import os
import re
import json
from getpass import getpass
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# Project root
ROOT = Path(__file__).parent

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Terminal Colors & Formatting
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class C:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


def header(text: str):
    """Print a section header."""
    width = 60
    print(f"\n{C.BOLD}{C.CYAN}{'━' * width}{C.END}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.END}")
    print(f"{C.BOLD}{C.CYAN}{'━' * width}{C.END}\n")


def step(msg: str):
    """Print a step being performed."""
    print(f"{C.CYAN}{C.BOLD}▶{C.END} {msg}")


def success(msg: str):
    """Print a success message."""
    print(f"  {C.GREEN}✓{C.END} {msg}")


def warn(msg: str):
    """Print a warning message."""
    print(f"  {C.YELLOW}⚠{C.END} {msg}")


def error(msg: str):
    """Print an error message."""
    print(f"  {C.RED}✗{C.END} {msg}")


def info(msg: str):
    """Print an info message."""
    print(f"  {C.DIM}ℹ{C.END} {msg}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run(cmd: list, cwd: Path = ROOT, capture: bool = True, env=None) -> Tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd,
            capture_output=capture, text=True, timeout=300,
            env=env
        )
        output = (result.stdout or '') + (result.stderr or '')
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 5 minutes"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Version Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def bump_version_str(current: str, bump_type: str = "patch") -> str:
    """Compute the next version string."""
    parts = [int(p) for p in current.split(".")]
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")
    major, minor, patch = parts
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def set_version(new_version: str) -> str:
    """Update version in pyproject.toml and __init__.py. Returns old version."""
    # Update pyproject.toml
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text()
    old_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    old_version = old_match.group(1) if old_match else "unknown"
    content = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content, flags=re.MULTILINE
    )
    pyproject.write_text(content)

    # Update __init__.py
    init_file = ROOT / "src" / "msd_sdk" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        content = re.sub(
            r'^__version__\s*=\s*"[^"]+"',
            f'__version__ = "{new_version}"',
            content, flags=re.MULTILINE
        )
        init_file.write_text(content)

    return old_version


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PyPI Queries
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_pypi_versions() -> Optional[list]:
    """Fetch published versions from PyPI. Returns None if package not found."""
    try:
        with urlopen("https://pypi.org/pypi/msd-sdk/json", timeout=10) as resp:
            data = json.loads(resp.read())
            return sorted(data.get("releases", {}).keys())
    except HTTPError as e:
        if e.code == 404:
            return None  # Package doesn't exist yet
        return None
    except (URLError, Exception):
        return None


def version_exists_on_pypi(version: str) -> Optional[bool]:
    """Check if a specific version exists on PyPI. Returns None if check failed."""
    versions = get_pypi_versions()
    if versions is None:
        return None
    return version in versions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Token Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_token() -> str:
    """Get PyPI token from environment or prompt."""
    token = os.environ.get("UV_PUBLISH_TOKEN") or os.environ.get("PYPI_TOKEN")

    if token:
        info(f"Using token from environment variable")
        return token

    print()
    try:
        token = getpass(f"  {C.BOLD}Enter your PyPI API token{C.END} (starts with pypi-): ")
    except (KeyboardInterrupt, EOFError):
        print("\n")
        sys.exit(0)

    if not token:
        error("No token provided")
        sys.exit(1)

    if not token.startswith("pypi-"):
        error("Token should start with 'pypi-'")
        sys.exit(1)

    return token


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build & Publish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def clean_dist():
    """Remove old dist files."""
    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        count = 0
        for f in dist_dir.glob("*.whl"):
            f.unlink()
            count += 1
        for f in dist_dir.glob("*.tar.gz"):
            f.unlink()
            count += 1
        if count:
            success(f"Cleaned {count} old dist file(s)")
    else:
        info("No dist/ directory to clean")


def build() -> bool:
    """Build the package with uv."""
    step("Building package...")

    ok, out = run(["uv", "build"])
    if ok:
        # Show built files
        dist_dir = ROOT / "dist"
        if dist_dir.exists():
            for f in dist_dir.iterdir():
                success(f"Built {f.name} ({f.stat().st_size / 1024:.1f} KB)")
        return True
    else:
        error("Build failed:")
        print(out)
        return False


def publish(token: str) -> bool:
    """Publish to PyPI."""
    step("Publishing to PyPI...")

    env = os.environ.copy()
    env["UV_PUBLISH_TOKEN"] = token

    ok, out = run(["uv", "publish"], env=env)
    if ok:
        return True
    else:
        error("Publish failed:")
        print(out)
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Publish Workflow
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def workflow_publish(bump_type: Optional[str] = None):
    """Main publish workflow."""
    header("MSD SDK → PyPI")

    version = get_version()

    # 1. Version bump (if requested)
    if bump_type:
        step(f"Bumping version ({bump_type})...")
        new_version = bump_version_str(version, bump_type)
        set_version(new_version)
        success(f"Version bumped: {version} → {C.BOLD}{new_version}{C.END}")
        version = new_version
        print()

    info(f"Version: {C.BOLD}v{version}{C.END}")
    info(f"Package: msd-sdk")
    print()

    # 2. Check if version already on PyPI
    step("Checking PyPI...")
    exists = version_exists_on_pypi(version)
    if exists is True:
        error(f"Version {version} already exists on PyPI!")
        print()
        next_version = bump_version_str(version, "patch")
        warn(f"Run with --bump to publish as v{next_version} instead:")
        info(f"python publish.py publish --bump")
        sys.exit(1)
    elif exists is False:
        success(f"Version {version} is not yet on PyPI — good to go")
    else:
        warn("Could not check PyPI (network issue?) — proceeding anyway")
    print()

    # 3. Clean + Build
    step("Cleaning old dist files...")
    clean_dist()
    print()

    if not build():
        sys.exit(1)
    print()

    # 4. Get token
    step("Authenticating...")
    token = get_token()
    print()

    # 5. Publish
    if not publish(token):
        sys.exit(1)

    # 6. Success
    print(f"\n{C.BOLD}{'━' * 60}{C.END}")
    print(f"{C.GREEN}{C.BOLD}  ✓ Published Successfully!{C.END}")
    print(f"{C.BOLD}{'━' * 60}{C.END}")
    print(f"\n  {C.CYAN}Package:{C.END}  msd-sdk v{version}")
    print(f"  {C.CYAN}URL:{C.END}      https://pypi.org/project/msd-sdk/{version}/")
    print(f"  {C.CYAN}Install:{C.END}  pip install msd-sdk=={version}")

    if bump_type:
        print(f"\n  {C.DIM}Don't forget to commit the version bump:{C.END}")
        print(f"  {C.DIM}  git add -A && git commit -m 'Release v{version}'{C.END}")

    print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Interactive Menu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def interactive_menu():
    """Show interactive menu to select publish mode."""
    header("MSD SDK Publisher")

    version = get_version()
    next_patch = bump_version_str(version, "patch")
    next_minor = bump_version_str(version, "minor")
    next_major = bump_version_str(version, "major")

    # Show current state
    print(f"  Current version: {C.BOLD}v{version}{C.END}")
    print(f"  Directory: {C.DIM}{ROOT}{C.END}")

    # Check PyPI status
    pypi_versions = get_pypi_versions()
    if pypi_versions is not None:
        latest = pypi_versions[-1] if pypi_versions else "(none published)"
        on_pypi = version in pypi_versions
        print(f"  PyPI latest: {C.DIM}{latest}{C.END}")
        if on_pypi:
            print(f"  Status: {C.YELLOW}v{version} already on PyPI — needs bump{C.END}")
        else:
            print(f"  Status: {C.GREEN}v{version} not yet published{C.END}")
    else:
        on_pypi = False
        print(f"  PyPI: {C.DIM}(could not check){C.END}")

    print()
    print(f"  {C.BOLD}What would you like to do?{C.END}")
    print()

    if not on_pypi:
        print(f"  {C.CYAN}[1]{C.END} {C.BOLD}Publish v{version}{C.END}")
        print(f"      {C.DIM}Build and upload the current version to PyPI.{C.END}")
        print()

    print(f"  {C.CYAN}[2]{C.END} {C.BOLD}Bump patch & Publish{C.END}  {C.DIM}(v{version} → v{next_patch}){C.END}")
    print(f"      {C.DIM}Increment patch version, then build and publish.{C.END}")
    print()
    print(f"  {C.CYAN}[3]{C.END} {C.BOLD}Bump minor & Publish{C.END}  {C.DIM}(v{version} → v{next_minor}){C.END}")
    print(f"      {C.DIM}Increment minor version, then build and publish.{C.END}")
    print()
    print(f"  {C.CYAN}[4]{C.END} {C.BOLD}Bump major & Publish{C.END}  {C.DIM}(v{version} → v{next_major}){C.END}")
    print(f"      {C.DIM}Increment major version, then build and publish.{C.END}")
    print()
    print(f"  {C.DIM}[q] Quit{C.END}")
    print()

    try:
        choice = input(f"  {C.BOLD}Enter choice [{('1-4' if not on_pypi else '2-4')}, q]:{C.END} ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n")
        sys.exit(0)

    if choice == '1' and not on_pypi:
        workflow_publish()
    elif choice == '2':
        workflow_publish(bump_type="patch")
    elif choice == '3':
        workflow_publish(bump_type="minor")
    elif choice == '4':
        workflow_publish(bump_type="major")
    elif choice in ('q', 'quit', 'exit'):
        print()
        sys.exit(0)
    else:
        error(f"Invalid choice: '{choice}'")
        sys.exit(1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Entry Point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_help():
    """Print help message."""
    print(__doc__)
    print("COMMANDS:")
    print("  publish    Build and publish to PyPI")
    print()
    print("OPTIONS:")
    print("  --bump [TYPE]   Bump version before publishing (patch/minor/major)")
    print("                  Defaults to 'patch' if TYPE is omitted")
    print("  --help, -h      Show this help message")
    print()
    print("ENVIRONMENT VARIABLES:")
    print("  UV_PUBLISH_TOKEN    PyPI API token (avoids interactive prompt)")
    print("  PYPI_TOKEN          Alternative env var for PyPI token")
    print()
    print("EXAMPLES:")
    print("  python publish.py                      # Interactive menu")
    print("  python publish.py publish               # Publish current version")
    print("  python publish.py publish --bump        # Bump patch + publish")
    print("  python publish.py publish --bump minor  # Bump minor + publish")
    print("  python publish.py publish --bump major  # Bump major + publish")
    print()


def main():
    """Main entry point."""
    args = sys.argv[1:]

    # Help flag
    if "--help" in args or "-h" in args:
        print_help()
        sys.exit(0)

    # Parse options
    bump_type = None
    if "--bump" in args:
        idx = args.index("--bump")
        if idx + 1 < len(args) and args[idx + 1] in ("patch", "minor", "major"):
            bump_type = args[idx + 1]
        else:
            bump_type = "patch"  # Default to patch

    # Filter out flags to get the command
    command_args = [a for a in args
                    if not a.startswith("-") and a not in ("patch", "minor", "major")]

    if not command_args:
        # No command — show interactive menu
        interactive_menu()
    elif command_args[0] == "publish":
        workflow_publish(bump_type=bump_type)
    else:
        error(f"Unknown command: {command_args[0]}")
        info("Use 'publish' or run without arguments for interactive mode.")
        info("Run 'python publish.py --help' for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
