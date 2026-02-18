# MSD SDK Tutorial — Hands On

*Sign it. Verify it. Trust it.*

This is a hands-on tutorial walking through everything the MSD SDK can do.
Every code block is **self-contained** — you can run any block on its own without running the ones before it.

> **Prerequisites:** `msd-sdk` and `zef` installed in the same virtual environment.


---

## 1. Your First Granule

A **Granule** is the fundamental unit of MSD: your data bundled together with metadata, a timestamp, and a cryptographic signature. Think of it as a tamper-proof envelope.

```python
import msd_sdk as msd

# A test key pair (never use this in production!)
my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

data = "Hello, MSD!"
metadata = {"author": "Tutorial", "purpose": "learning"}

granule = msd.create_granule(data, metadata, my_key)
granule
```
````Result
{
  '__type': 'ET.SignedGranule',
  'data': 'Hello, MSD!',
  'metadata': {'author': 'Tutorial', 'purpose': 'learning'},
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1771430628'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': (
      '🔏-3db2d49d7119790bfbfc0405cc2f3554d2e9b09695dfe2c63099a74cf3c7acc725e53d1ca10'
      'a6afdba0e9cc4cba03fb6556b1ac9922e9e0426e5147e708da50d'
    )
  },
  'key': {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
  }
}
````
````Side Effects
[]
````

The granule contains `data`, `metadata`, `signature_time`, `signature`, and `key` (public only — your private key never leaks).


---

## 2. Verify a Granule

The whole point of signing is that anyone can check: *was this data tampered with?*

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

granule = msd.create_granule(
    {"temperature": 22.5, "unit": "celsius"},
    {"sensor": "living-room", "version": "1.0"},
    my_key
)

# Verify — should be True
print("Valid:", msd.verify(granule))

# Sign the same metadata but with different data
different_data_granule = msd.create_granule(
    {"temperature": 99.9, "unit": "celsius"},
    {"sensor": "living-room", "version": "1.0"},
    my_key
)
# Still valid — it's a properly signed granule, just with different data
("Also valid:", msd.verify(different_data_granule))
```
````Result
('Also valid:', True)
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='Valid:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='True'
    )
]
````

Both return `True` because both were properly signed. To see what happens when data is *tampered with after signing*, check out Section 6 below — it demonstrates tamper detection in detail.


---

## 3. Content Hashing

Sometimes you don't need a signature — you just want a content-addressable hash. MSD uses BLAKE3 Merkle hashing, which means dicts and lists are hashed structurally (by their elements), not just as raw bytes.

```python
import msd_sdk as msd

# Same content → same hash
h1 = msd.content_hash("Hello, World!")
h2 = msd.content_hash("Hello, World!")
print(f"hash 1: {h1}")
print(f"hash 2: {h2}")
print(f"Same content, same hash: {h1 == h2}")

# Different content → different hash
h3 = msd.content_hash("Hello, World?")
print(f"Different content, different hash: {h1 != h3}")

# Works on complex structures too
h4 = msd.content_hash({"name": "Alice", "scores": [95, 87, 92]})
("Dict hash:", h4)
```
````Result
('Dict hash:', Dict('🪨-46f6db59fa31299d411d927e2b0cf0f4810c7b007270d998a80fe40e21a79ed3'))
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='hash 1: String(hash=\'🪨-47226ebc134d64d9dd49990d23ddf503794b9e972d4981bb2f9a984301c1ae5c\')'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='hash 2: String(hash=\'🪨-47226ebc134d64d9dd49990d23ddf503794b9e972d4981bb2f9a984301c1ae5c\')'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Same content, same hash: True'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Different content, different hash: True'
    )
]
````


---

## 4. Signing Dicts — The Invisible Signature 🔏

Granules are great for storage and transmission, but sometimes you just want to sign an existing Python dict without changing its shape. `sign_and_embed_dict` tucks the signature away in a special `__msd` key, encoded as invisible Unicode variation selectors inside an emoji. The dict stays clean and human-readable.

```python
import msd_sdk as msd
import json

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

recipe = {
    "name": "Pancakes",
    "servings": 4,
    "ingredients": ["flour", "eggs", "milk", "butter"],
    "approved_by": "Chef Tutorial"
}

signed = msd.sign_and_embed_dict(
    recipe,
    {"author": "Chef Tutorial", "license": "CC-BY-4.0"},
    my_key
)

# The original data is untouched + there's a new __msd key
print("Keys:", list(signed.keys()))
print("Name:", signed["name"])
print("Servings:", signed["servings"])

# The __msd value looks like a single emoji to the naked eye
msd_val = signed["__msd"]
print(f"__msd starts with: {msd_val[:1]}")
print(f"__msd length: {len(msd_val)} characters (the signature is hidden in there!)")

# It survives JSON round-trips
json_str = json.dumps(signed)
recovered = json.loads(json_str)
("Survived JSON roundtrip:", '__msd' in recovered)
```
````Result
('Survived JSON roundtrip:', True)
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='Keys:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='[\'name\', \'servings\', \'ingredients\', \'approved_by\', \'__msd\']'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Name:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Pancakes'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Servings:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='4'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='__msd starts with: 🔏'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='__msd length: 437 characters (the signature is hidden in there!)'
    )
]
````


---

## 5. Reading What's Hidden

You can extract the metadata and signature from a signed dict:

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

signed = msd.sign_and_embed_dict(
    {"project": "Apollo", "status": "launched"},
    {"team": "Mission Control", "classification": "public"},
    my_key
)

# Extract just the metadata
meta = msd.extract_metadata(signed)
print("Metadata:", meta)

# Extract the full signature details
sig = msd.extract_signature(signed)
print("Signature time:", sig["signature_time"])
("Signed by key:", sig["key"]["__uid"])
```
````Result
('Signed by key:', '🍃-8d1dc8766070c87a4bb1')
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='Metadata:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='{\'team\': \'Mission Control\', \'classification\': \'public\'}'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Signature time:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='{\'__type\': \'Time\', \'zef_unix_time\': \'1771429592\'}'
    )
]
````


---

## 6. Tamper-Proof Dicts

`verify()` works on signed dicts too. Change anything in the data — a value, add a key, remove a key — and the signature breaks.

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

original = {"score": 42, "player": "Alice"}
signed = msd.sign_and_embed_dict(original, {"game": "tutorial"}, my_key)

# Untouched: valid
print("Original:", msd.verify(signed))

# Tamper 1: change a value
tampered = dict(signed)
tampered["score"] = 9999
print("Changed score:", msd.verify(tampered))

# Tamper 2: add a key
tampered2 = dict(signed)
tampered2["cheated"] = True
print("Added key:", msd.verify(tampered2))

# Tamper 3: remove a key
tampered3 = {k: v for k, v in signed.items() if k != "player"}
("Removed key:", msd.verify(tampered3))
```
````Result
('Removed key:', False)
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='Original:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='True'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Changed score:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='False'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Added key:'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content=' '
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='False'
    )
]
````


All three tampering attempts return `False`. The cryptographic signature is unforgeable.


---

## 7. Signing Binary Files

MSD can embed signatures directly into image and document files. The signed file remains viewable by standard programs — the signature is tucked into format-specific metadata regions.

Supported formats: **PNG, JPG, PDF, DOCX, XLSX, PPTX**.

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

# Create a minimal valid 1x1 red PNG (67 bytes)
import struct, zlib
def make_tiny_png():
    sig = b'\x89PNG\r\n\x1a\n'
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw = zlib.compress(b'\x00\xff\x00\x00')  # filter byte + 1 red pixel
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', raw) + chunk(b'IEND', b'')

png_bytes = make_tiny_png()
print(f"Original PNG: {len(png_bytes)} bytes")

# Sign and embed
signed_png = msd.sign_and_embed(
    {'type': 'png', 'content': png_bytes},
    {'author': 'Tutorial', 'description': 'A very small red square'},
    my_key
)
print(f"Signed PNG: {len(signed_png['content'])} bytes")

# Extract metadata from the signed file
meta = msd.extract_metadata(signed_png)
print(f"Embedded metadata: {meta}")

# Verify the signature
print(f"Valid: {msd.verify(signed_png)}")

# Strip the signature to recover the original
clean = msd.strip_metadata_and_signature(signed_png)
print(f"Stripped PNG: {len(clean['content'])} bytes")
("Content matches original:", clean['content'] == png_bytes)
```
````Result
('Content matches original:', True)
````
````Side Effects
[
    ET.UnmanagedEffect(
        what='stdout',
        content='Original PNG: 69 bytes'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Signed PNG: 460 bytes'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Embedded metadata: {\'author\': \'Tutorial\', \'description\': \'A very small red square\'}'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Valid: True'
    ),
    ET.UnmanagedEffect(
        what='stdout',
        content='Stripped PNG: 69 bytes'
    )
]
````


---

## Quick Reference

| What you want to do | Function |
|---|---|
| Sign any data into a granule | `msd.create_granule(data, metadata, key)` |
| Sign a dict (invisible signature) | `msd.sign_and_embed_dict(data, metadata, key)` |
| Sign a file (PNG, PDF, etc.) | `msd.sign_and_embed({'type': ..., 'content': ...}, metadata, key)` |
| Verify any signed data | `msd.verify(signed_data)` |
| Extract metadata | `msd.extract_metadata(signed_data)` |
| Extract signature info | `msd.extract_signature(signed_data)` |
| Content hash (no signing) | `msd.content_hash(data)` |
| Strip signature from file | `msd.strip_metadata_and_signature(signed_file)` |
| Load key from env var | `msd.key_from_env("MSD_PRIVATE_KEY")` |
