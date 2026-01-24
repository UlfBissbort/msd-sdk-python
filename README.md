# MSD SDK

Python SDK for Meta Structured Data.

📖 **[Read the full SDK overview](docs/overview.md)** for architecture, design decisions, and detailed documentation.

## Installation

```bash
pip install msd-sdk
```

## Usage

```python
import msd-sdk as msd
my_key = msd.key_from_env("MSD_PRIVATE_KEY")
```

The imported key is of the plain data form
```python
my_key = {
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}
```

```python
metadata={
    'creator': 'Alice',
    'description': 'sample data',
}

my_granule = msd.create_granule(data, metadata, my_key)
```

The returned granule is a plain data and contains the data, metadata, timestamp and signature.
```python
{
  '__type': 'ET.SignedGranule',
  'data': 'Hello, Meta Structured Data!',
  'metadata': {'creator': 'Alice', 'description': 'sample data'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1769247801'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': (
      '🔏-9ca87607f2b7357e82453224bee6f15327d566836e1f3eb0af31149f496ced94d2b6127e89a'
      'b7a63a2470d23210e00090dbe9766c76072f911ed6bd00ac5fc04'
    )
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
```



```python
# content hash only
my_content_hash = msd.content_hash(data)

# verifying signatures
is_valid = msd.verify(signed_bundle)    # returns True/False
```




## License

Licensed under either of:

- MIT license ([LICENSE](LICENSE) or http://opensource.org/licenses/MIT)
- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)

at your option.




```python
from zef import *

my_key = {
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

data="Hello, Meta Structured Data!"
metadata={
    'creator': 'Alice',
    'description': 'sample data',
}
timestamp = now()


# my_key | from_json_like | remove('private_key') | collect
create_signed_granule(data, metadata, timestamp, from_json_like(my_key)) | to_json_like | collect


```
````Result
{
  '__type': 'ET.SignedGranule',
  'data': 'Hello, Meta Structured Data!',
  'metadata': {'creator': 'Alice', 'description': 'sample data'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1769247795.03406592'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': (
      '🔏-2406ff6af58a5c72878ee0f2df374cd63396c0adaca6905b2d1881ca45442658fa49baac780'
      '2fc464ec8f51f8f102943137c59d71b3e908609b356deb118dc0c'
    )
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
````
````Side Effects
[]
````