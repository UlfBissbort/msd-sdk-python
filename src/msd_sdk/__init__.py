"""MSD SDK - Python SDK for Meta Structured Data"""

__version__ = "0.1.1"


def _verify_zef_installation():
    """Verify that the correct zef (rust-based) is installed."""
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


# Verify zef installation on import
_zef = _verify_zef_installation()


# Re-export core API functions
from msd_sdk.core import (
    key_from_env,
    create_granule,
    content_hash,
    verify,
)

__all__ = [
    "__version__",
    "key_from_env",
    "create_granule", 
    "content_hash",
    "verify",
]



