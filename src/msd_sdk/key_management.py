"""
Key Management for MSD SDK

Generate, store, and manage Ed25519 key pairs with endorsement chains.
Keys are plain data (dicts) - you control naming and storage.
"""

import os
import sys
from typing import Optional


def generate_key_pair(
    endorsed_by: Optional[dict] = None,
    expires_in: Optional[str] = None,
) -> dict:
    """
    Generate a new Ed25519 key pair.
    
    With no arguments, creates an identity key endorsed by the MSD platform.
    With `endorsed_by`, creates a working key endorsed by the given key.
    
        # Identity key (platform-endorsed, never expires)
        identity = msd.generate_key_pair()
        
        # Working key (endorsed by identity, expires in 30 days)
        working = msd.generate_key_pair(endorsed_by=identity, expires_in="30d")
    
    Duration units: "1h" (hours), "7d" (days), "3m" (months)
    
    Returns a key dict with __type, __uid, public_key, private_key,
    and either platform_certificate or endorsement.
    """
    raise NotImplementedError("generate_key_pair is not yet implemented")


def save_key(name_or_path: str, key: dict) -> str:
    """
    Save a key to disk as JSON.
    
    If `name_or_path` is a simple name (no slashes), saves to the
    OS-appropriate default directory:
    
        msd.save_key("alice.json", key)
        # → ~/.config/msd/keys/alice.json (macOS/Linux)
        # → %APPDATA%\\msd\\keys\\alice.json (Windows)
    
    If `name_or_path` is a full path, saves there directly:
    
        msd.save_key("/secure/keys/alice.json", key)
    
    Returns the full path where the key was saved.
    """
    raise NotImplementedError("save_key is not yet implemented")


def load_key(name_or_path: str) -> dict:
    """
    Load a key from disk.
    
    Mirrors `save_key` - simple names use the default directory,
    full paths are used directly.
    
        key = msd.load_key("alice.json")
        key = msd.load_key("/secure/keys/alice.json")
    
    Returns the key dict.
    """
    raise NotImplementedError("load_key is not yet implemented")


def get_key_directory() -> str:
    """
    Get the default key storage directory for the current OS.
    
        msd.get_key_directory()
        # → "~/.config/msd/keys/" (macOS/Linux)
        # → "%APPDATA%\\msd\\keys\\" (Windows)
    
    Returns the expanded absolute path.
    """
    if sys.platform == "win32":
        # Windows: use APPDATA, fall back to home if not set
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "msd", "keys")
    else:
        # macOS/Linux: XDG-style config directory
        return os.path.join(os.path.expanduser("~"), ".config", "msd", "keys")


def is_endorsed(key: dict) -> bool:
    """
    Check if a key is endorsed by a trusted root.
    
    Traces the endorsement chain from the key up to a trust anchor.
    Returns True if the chain is valid and ends at a trusted root.
    
        if msd.is_endorsed(key):
            print("Key is part of a valid endorsement chain")
    """
    raise NotImplementedError("is_endorsed is not yet implemented")


def get_endorsement_chain(key: dict) -> list:
    """
    Get the full endorsement chain for a key.
    
    Returns a list from root to key, showing who endorsed whom:
    
        chain = msd.get_endorsement_chain(working_key)
        # [
        #     {'type': 'MSD Platform Root', 'uid': '🍃-...', 'status': 'trusted'},
        #     {'type': 'Identity Key', 'uid': '🍃-...', 'endorsed_by': '🍃-...'},
        #     {'type': 'Working Key', 'uid': '🍃-...', 'endorsed_by': '🍃-...'}
        # ]
    """
    raise NotImplementedError("get_endorsement_chain is not yet implemented")


def add_trust_anchor(name: str, public_key: str) -> None:
    """
    Add a custom trust anchor.
    
    By default, only the MSD platform root is trusted. Add custom
    anchors to trust keys from other organizations:
    
        msd.add_trust_anchor(
            name="Acme Corp",
            public_key="🔑-a1b2c3d4e5f67890..."
        )
    
    After adding, keys endorsed by Acme's root will be considered trusted.
    """
    raise NotImplementedError("add_trust_anchor is not yet implemented")
