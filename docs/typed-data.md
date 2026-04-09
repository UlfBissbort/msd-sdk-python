# Typed Data in MSD SDK

Binary files and media types are represented as **typed dicts** — plain Python dicts with a `__type` field that tells the SDK what kind of data it is.

## Format

```python
{'__type': 'PngImage', 'data': '<base64-encoded bytes>'}
```

The `__type` field is a **type sentinel**: a dict with `__type` is treated as that specific data type, not as a regular dictionary.

The `data` field contains the payload — base64-encoded for binary types, or a plain string for text types like SVG.

## Supported Types

| `__type` | Format | Description |
|---|---|---|
| `PngImage` | base64 | PNG image |
| `JpgImage` | base64 | JPEG image |
| `WebpImage` | base64 | WebP image |
| `SvgImage` | text | SVG image (XML string) |
| `PDF` | base64 | PDF document |
| `WordDocument` | base64 | Word document (DOCX) |
| `ExcelDocument` | base64 | Excel spreadsheet (XLSX) |
| `PowerpointDocument` | base64 | PowerPoint presentation (PPTX) |

## Creating Typed Data

```python
import base64

# From a file on disk
with open('photo.png', 'rb') as f:
    png_data = {'__type': 'PngImage', 'data': base64.b64encode(f.read()).decode()}

# From bytes in memory
jpg_data = {'__type': 'JpgImage', 'data': base64.b64encode(jpg_bytes).decode()}

# SVG is text — no base64 needed
svg_data = {'__type': 'SvgImage', 'data': '<svg><rect width="100" height="100" fill="blue" /></svg>'}
```

## Using Typed Data Throughout the SDK

Typed dicts work everywhere in the SDK:

### Signing and Embedding

```python
import msd_sdk as msd

key = msd.generate_key_pair(unendorsed=True)

signed = msd.sign(
    {'__type': 'PngImage', 'data': png_b64},
    {'author': 'Alice', 'description': 'Photo'},
    key
)
signed_png = msd.embed(signed)
# Returns: {'__type': 'PngImage', 'data': '<base64 with embedded signature>'}
```

### Verification

```python
result = msd.verify(signed_png)
result['signature_is_valid']  # True
```

### Extracting Metadata and Signature

```python
meta = msd.extract_metadata(signed_png)
# {'author': 'Alice', 'description': 'Photo'}

sig_info = msd.extract_signature(signed_png)
# {'signature': {...}, 'signature_time': {...}, 'key': {...}}
```

### Stripping Signatures

```python
clean = msd.strip_metadata_and_signature(signed_png)
# {'__type': 'PngImage', 'data': '<original base64>'}
```

### Content Hashing

```python
h = msd.content_hash({'__type': 'PngImage', 'data': png_b64})
# {'__type': 'MsdHash', 'hash': '7a3f1e...'}
```

### In Signed Data

```python
signed = msd.sign(
    {'__type': 'PngImage', 'data': png_b64},
    {'photographer': 'Bob'},
    key
)
result = msd.verify(signed)
result['signature_is_valid']  # True
```

## Saving Signed Files to Disk

```python
import base64

# Sign
signed = msd.sign(
    {'__type': 'PngImage', 'data': base64.b64encode(open('input.png', 'rb').read()).decode()},
    {'author': 'Alice'},
    key
)
signed_file = msd.embed(signed)

# Save signed file
with open('signed.png', 'wb') as f:
    f.write(base64.b64decode(signed_file['data']))

# The signed file is a valid PNG — viewable in any image viewer,
# but also carries the cryptographic signature.
```

## The `__type` Convention

`__type` is a reserved key in the MSD SDK. Any dict with `__type` set to a recognized type name is treated as typed data, not as a plain dictionary.

This means:

- `{'__type': 'PngImage', 'data': '...'}` → treated as a PNG image
- `{'message': 'hello'}` → treated as a regular dict
- `{'__type': 'ET.SignedData', ...}` — treated as signed data

If you have data that happens to have an `__type` key matching a recognized type name, it will be interpreted as that type. Rename the key to avoid collisions.
