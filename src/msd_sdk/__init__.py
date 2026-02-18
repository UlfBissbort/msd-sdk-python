"""
MSD SDK - Sign and verify structured data with Ed25519 signatures.

Quick Start
-----------
    import msd_sdk as msd
    
    key = msd.generate_key_pair()
    signed = msd.create_granule({"msg": "hello"}, {"author": "alice"}, key)
    assert msd.verify(signed)

Core Functions
--------------
    create_granule     - Sign data with metadata, returns a granule
    verify             - Verify a granule's signature
    content_hash       - Get BLAKE3 Merkle hash of any data

Key Management
--------------
    generate_key_pair  - Create identity or working keys
    save_key           - Save key to file (JSON format)
    load_key           - Load key from file
    key_from_env       - Load key from environment variable
    get_key_directory  - Get OS-appropriate key storage path
    is_endorsed        - Check if key has valid endorsement chain
    get_endorsement_chain - Get full chain from root to key

File Embedding
--------------
    sign_and_embed     - Embed signature in PNG/JPG/PDF/DOCX/XLSX/PPTX
    extract_metadata   - Read embedded metadata from file
    extract_signature  - Read embedded signature from file
    strip_metadata_and_signature - Remove embedded data, get original

Documentation: See docs/overview.md and docs/key-management.md
"""

__version__ = "0.1.4"


def _verify_zef_installation():
    """
    Verify that the correct zef (rust-based) is installed.
    
    This is called at import time to fail fast if the required
    zef-core package is not available.
    """
    try:
        import zef
    except ImportError:
        raise ImportError(
            "msd-sdk requires the zef package (rust-based zef-core). "
            "This is currently not publicly available yet. Coming soon."
        )
    
    # Check for blake3_hash which is only available in rust-based zef
    if not hasattr(zef, 'blake3_hash'):
        raise ImportError(
            "msd-sdk requires the rust-based zef package (zef-core), "
            "but a different 'zef' package is installed. "
            "The required Zef package is not publicly available yet. Coming soon."
        )
    
    return zef


# Verify zef installation at import time (fail fast)
_zef = _verify_zef_installation()


# Re-export core API functions from the core module.
# This provides a flat API: users write `msd.create_granule()` instead of
# `msd.core.create_granule()`. The actual implementations live in core.py
# for better code organization.
from msd_sdk.core import (
    key_from_env,
    create_granule,
    content_hash,
    verify,
    sign_and_embed,
    sign_and_embed_dict,
    extract_metadata,
    extract_signature,
    strip_metadata_and_signature,
)

# Re-export key management functions
from msd_sdk.key_management import (
    generate_key_pair,
    save_key,
    load_key,
    get_key_directory,
    is_endorsed,
    get_endorsement_chain,
)

# __all__ explicitly declares the public API of this package.
# When users write `from msd_sdk import *`, only these names are imported.
# Internal helpers like _verify_zef_installation and _zef are excluded.
__all__ = [
    "__version__",
    # Core API
    "key_from_env",
    "create_granule", 
    "content_hash",
    "verify",
    "sign_and_embed",
    "sign_and_embed_dict",
    "extract_metadata",
    "extract_signature",
    "strip_metadata_and_signature",
    # Key Management
    "generate_key_pair",
    "save_key",
    "load_key",
    "get_key_directory",
    "is_endorsed",
    "get_endorsement_chain",
]



