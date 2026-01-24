# MSD SDK

Python SDK for Meta Structured Data.

## Installation

```bash
pip install msd-sdk
```

## Usage

```python
import msd-sdk as msd
my_key = msd.key_from_env("MSD_PRIVATE_KEY")

metadata={
    'creator': 'Alice',
    'description': 'sample data',
    'timestamp': '2024-10-01T12:00:00Z'
}

my_granule = msd.create_granule(data, metadata, my_key)

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
