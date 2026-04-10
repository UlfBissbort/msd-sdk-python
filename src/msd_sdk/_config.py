"""Shared MSD config root resolution.

All MSD persistent state lives under one directory:
  - macOS/Linux: ~/.config/msd/ (or $XDG_CONFIG_HOME/msd/)
  - Windows: %APPDATA%\\msd\\
"""

from __future__ import annotations
import os
import sys


def get_msd_config_root() -> str:
    """Get the MSD config root directory, respecting XDG on Linux/macOS."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "msd")

    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return os.path.join(xdg_config, "msd")
    return os.path.join(os.path.expanduser("~"), ".config", "msd")
