# MSD SDK

Python SDK for Meta Structured Data.

📖 **[Read the full SDK overview](docs/overview.md)** for architecture, design decisions, and detailed documentation.

## Installation

```bash
pip install msd-sdk
```

> **Note**: This SDK requires `zef-core` which is not yet publicly available. The import will fail until zef-core is installed.

## Development: Building from Source

When developing locally, you must build and install from the local wheel to avoid pip installing the (older) PyPI version.

```bash
# 1. Build the wheel
uv build

# 2. Install from local dist (not from PyPI!)
#    Use --no-index to prevent PyPI fallback
python -m pip install --no-index --find-links=./dist msd-sdk

# Or with explicit path to avoid version conflicts:
python -m pip install ./dist/msd_sdk-*.whl --force-reinstall
```

**Common Pitfall**: Running `pip install .` may reinstall the published PyPI version if it has the same version number. Always use `--no-index` or install the wheel directly when developing.

## Usage

### 1. Load Key from Environment

The key must be stored as a JSON string in an environment variable:

```python
import msd_sdk as msd

my_key = msd.key_from_env("MSD_PRIVATE_KEY")
```

**Key structure returned:**
```python
{
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}
```

### 2. Create a Signed Granule

**Important:**
- `data` can be **any plain data type**: string, dict, list, number, boolean, etc.
- `metadata` must always be a **dictionary**

#### Example 1: String data

```python
data = "Hello, Meta Structured Data!"
metadata = {
    'creator': 'Alice',
    'description': 'sample data',
}

my_granule = msd.create_granule(data, metadata, my_key)
```

**Granule structure returned:**
```python
{
  '__type': 'ET.SignedGranule',
  'data': 'Hello, Meta Structured Data!',
  'metadata': {'creator': 'Alice', 'description': 'sample data'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': '🔏-9f3a8c29e9784fe63ccc7ebc3e1f394e9dcdf9a7d51bc6fa314dac8a902e9aff6a4e64619bae5a4f674980fcba77877d8a0131e8dfa7976cc23cf1d526ab0c07'
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
```

#### Example 2: Dict data (nested structures supported)

```python
data = {"message": "Hello", "count": 42, "nested": {"key": "value"}}
metadata = {'creator': 'Bob', 'schema': 'v1.0'}

my_granule = msd.create_granule(data, metadata, my_key)
```

**Granule structure returned:**
```python
{
  '__type': 'ET.SignedGranule',
  'data': {'message': 'Hello', 'count': 42, 'nested': {'key': 'value'}},
  'metadata': {'creator': 'Bob', 'schema': 'v1.0'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': '🔏-04ae2907139456ea20a5d0812dfb14ff90abe010113142cbdfd1b8703aea0fc5bd2791249049789983d39f8c63851fb4175fec52993f7ea500931fd7eac32506'
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
```

### 3. Verify a Granule

```python
is_valid = msd.verify(my_granule)  # returns True or False
```

Returns `True` if the signature is valid for the data, `False` if tampered.

### 4. Content Hash (without signature)

```python
my_content_hash = msd.content_hash(data)
# Returns: String(hash='🪨-523d1d9f304a40f30aa741cbdd66cad80f65b9db6c6cba66f2e149e0c2907f29')
```




## License

Licensed under either of:

- MIT license ([LICENSE](LICENSE) or http://opensource.org/licenses/MIT)
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)

at your option.


