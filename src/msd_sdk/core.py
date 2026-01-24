"""Core API functions for MSD SDK."""

import json


def key_from_env(env_var_name: str = "MSD_PRIVATE_KEY") -> dict:
    """
    Load an Ed25519 key pair from an environment variable.
    
    The environment variable should contain a JSON-encoded key pair.
    
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
        KeyError: If the environment variable is not set.
        json.JSONDecodeError: If the environment variable doesn't contain valid JSON.
    """
    import zef
    
    # Use Zef's managed effect system to get the environment variable
    env_value = zef.FX.GetEnvVar(name=env_var_name) | zef.run
    
    if env_value is None:
        raise KeyError(f"Environment variable '{env_var_name}' is not set")
    
    # Convert Zef String to Python string and parse as JSON
    key_json = str(env_value)
    return json.loads(key_json)


def create_granule(data, metadata: dict, key: dict) -> dict:
    """
    Create a signed MSD Granule.
    
    A Granule is the fundamental unit in MSD: a piece of data combined with
    its metadata, timestamp, and cryptographic signature.
    
    Args:
        data: The data to sign (can be any JSON-serializable value).
        metadata: A dictionary of metadata about the data.
        key: The Ed25519 key pair to sign with (from key_from_env or similar).
             Must be a dict with '__type': 'ET.Ed25519KeyPair' and 'private_key'.
    
    Returns:
        A dictionary representing the signed granule with structure:
        {
          '__type': 'ET.SignedGranule',
          'data': ...,
          'metadata': {...},
          'signature_time': {...},
          'signature': {...},
          'key': {...}
        }
    """
    import zef
    timestamp = zef.now()
    key_internal = zef.from_json_like(key)
    granule_internal = zef.create_signed_granule(data, metadata, timestamp, key_internal)
    result = granule_internal | zef.to_json_like | zef.collect
    return result


def content_hash(data) -> str:
    """
    Compute the BLAKE3 content hash of data.
    
    Args:
        data: The data to hash (can be any JSON-serializable value).
    
    Returns:
        A string representing the content hash in the format '🪨-{hex}'.
    """
    import zef
    return zef.merkle_hash(data)


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
