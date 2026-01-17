# User Facing MSD Python SDK


### Signing Data
```python
import metastructured as msd
from msd.keys import acme_key

signature_only = sign(my_json_data, acme_key)

signed_bundle = sign_to_granite(my_json_data, acme_key)  # in json-like format

my_content_hash = content_hash(my_json_data)   # only hash
```

### Verifying Signatures
```python
verify_siganture(signed_bundle)    # returns True/False
```