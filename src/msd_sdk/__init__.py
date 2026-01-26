"""
MSD SDK - Python SDK for Meta Structured Data

Package Structure & Import System Explanation
=============================================

This __init__.py serves as the public interface for the msd_sdk package.
Here's how Python's import system works with this module:

1. PACKAGE INITIALIZATION:
   When you write `import msd_sdk`, Python executes this __init__.py file.
   Everything defined or imported here becomes accessible as `msd_sdk.xxx`.

2. RE-EXPORTING FROM SUBMODULES:
   The core functions (key_from_env, create_granule, etc.) are defined in
   `msd_sdk/core.py` but we import and re-export them here. This allows:
   
       import msd_sdk as msd
       msd.create_granule(...)  # Works! Even though it's defined in core.py
   
   This pattern keeps the implementation organized in separate files while
   providing a clean, flat API to users.

3. THE __all__ LIST:
   __all__ defines what gets exported when someone writes:
   
       from msd_sdk import *
   
   Only names listed in __all__ will be imported. This:
   - Prevents internal/private names from polluting the namespace
   - Documents the public API explicitly
   - Allows linters to warn about unused imports

4. EAGER ZEF VERIFICATION:
   The zef dependency is verified at import time. If zef-core is not
   installed, the import will fail immediately with a clear error message.
   This ensures users know about the missing dependency right away.

Usage Examples:
    # Standard import (recommended)
    import msd_sdk as msd
    msd.create_granule(data, metadata, key)
    
    # Direct function import
    from msd_sdk import create_granule, verify
    create_granule(data, metadata, key)
    
    # Star import (uses __all__)
    from msd_sdk import *
    create_granule(data, metadata, key)  # Available
    _zef  # Not available (not in __all__)
"""

__version__ = "0.1.2"


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
    extract_metadata,
    extract_signature,
    strip_metadata_and_signature,
)

# __all__ explicitly declares the public API of this package.
# When users write `from msd_sdk import *`, only these names are imported.
# Internal helpers like _verify_zef_installation and _zef are excluded.
__all__ = [
    "__version__",
    "key_from_env",
    "create_granule", 
    "content_hash",
    "verify",
    "sign_and_embed",
    "extract_metadata",
    "extract_signature",
    "strip_metadata_and_signature",
]



