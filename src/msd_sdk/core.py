"""Core API functions for MSD SDK."""


def key_from_env(env_var_name: str = "MSD_PRIVATE_KEY") -> dict:
    """
    Load an Ed25519 key pair from an environment variable.
    
    Args:
        env_var_name: Name of the environment variable containing the key.
                      Defaults to "MSD_PRIVATE_KEY".
    
    Returns:
        A dictionary representing the key pair with structure:
        {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-...',
          'private_key': '🗝️-...',
          'public_key': '🔑-...'
        }
    
    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "key_from_env is not yet implemented. "
        "This function will load an Ed25519 key pair from the specified environment variable."
    )


def create_granule(data, metadata: dict, key: dict) -> dict:
    """
    Create a signed MSD Granule.
    
    A Granule is the fundamental unit in MSD: a piece of data combined with
    its metadata, timestamp, and cryptographic signature.
    
    Args:
        data: The data to sign (can be any JSON-serializable value).
        metadata: A dictionary of metadata about the data.
        key: The Ed25519 key pair to sign with (from key_from_env or similar).
    
    Returns:
        A dictionary representing the signed granule with structure:
        {
          '__type': 'MSD.Granule',
          'data': ...,
          'metadata': {...},
          'signature_time': {...},
          'signature': {...},
          'key': {...}
        }
    
    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "create_granule is not yet implemented. "
        "This function will create a signed MSD Granule from data, metadata, and a key."
    )


def content_hash(data) -> str:
    """
    Compute the BLAKE3 content hash of data.
    
    Args:
        data: The data to hash (can be any JSON-serializable value).
    
    Returns:
        A string representing the content hash in the format '🪨-{hex}'.
    
    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "content_hash is not yet implemented. "
        "This function will compute the BLAKE3 merkle hash of the provided data."
    )


def verify(granule: dict) -> bool:
    """
    Verify the signature of an MSD Granule.
    
    Args:
        granule: A signed granule dictionary (from create_granule or loaded from storage).
    
    Returns:
        True if the signature is valid, False otherwise.
    
    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "verify is not yet implemented. "
        "This function will verify the Ed25519 signature of an MSD Granule."
    )
