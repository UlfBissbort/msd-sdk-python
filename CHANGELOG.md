# Changelog

All notable changes to the MSD SDK are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — Sign. Embed. Verify.

### Breaking Changes

- **Removed `create_granule()`** — use `sign(data, metadata, key)` instead. Returns `ET.SignedData` (not `ET.SignedGranule`).

- **Removed `sign_and_embed()`** and **`sign_and_embed_dict()`** — use `sign()` then `embed()` as two separate steps.

  Before:
  ```python
  signed_dict = msd.sign_and_embed_dict(data, metadata, key)
  signed_file = msd.sign_and_embed(typed_data, metadata, key)
  ```

  After:
  ```python
  signed = msd.sign(data, metadata, key)
  embedded_dict = msd.embed(signed)          # for dicts
  embedded_file = msd.embed(signed)          # for typed file data
  ```

- **`verify()` now returns a rich dict instead of a boolean.**

  Before:
  ```python
  is_valid = msd.verify(signed_data)  # True/False
  ```

  After:
  ```python
  result = msd.verify(signed_data)
  result['signature_is_valid']  # True/False
  # Also: data_hash, metadata_hash, signature_timestamp, signing_key, etc.
  ```

- **`verify()` rejects `ET.SignedGranule`** — only accepts `ET.SignedData`. Raises `ValueError` with migration guidance.

- **`sign()` strips embedded data from typed files before signing** — re-signing an already-embedded file produces a clean signature over the original content.

### Added

- `sign(data, metadata, key)` — create a signed data envelope
- `embed(signed_data)` — embed signature into data (dict steganography or file binary embedding)

---

## [Unreleased]

### Breaking Changes

- **`content_hash()` now returns a dict instead of a plain hex string.**

  Before (0.1.7):
  ```python
  msd.content_hash("hello")
  # '928d2f9f582b4423e27990762d3ce78ab9106a1aa7001f998b0378a941850f38'
  ```

  After:
  ```python
  msd.content_hash("hello")
  # {'__type': 'MsdHash', 'hash': '928d2f9f582b4423e27990762d3ce78ab9106a1aa7001f998b0378a941850f38'}
  ```

  **Migration:** Replace `msd.content_hash(x)` with `msd.content_hash(x)['hash']` where a plain hex string is needed.

- **File data now uses typed dicts with `__type` instead of `{'type': ..., 'content': bytes}`.**

  Before (0.1.7):
  ```python
  msd.sign_and_embed({'type': 'png', 'content': png_bytes}, metadata, key)
  # returned: {'type': 'png', 'content': signed_bytes}
  ```

  After:
  ```python
  import base64
  msd.sign_and_embed({'__type': 'PngImage', 'data': base64.b64encode(png_bytes).decode()}, metadata, key)
  # returns: {'__type': 'PngImage', 'data': '<base64>'}
  ```

  All file functions (`sign_and_embed`, `verify`, `extract_metadata`, `extract_signature`, `strip_metadata_and_signature`, `content_hash`, `create_granule`) now use the typed dict format. Supported types: `PngImage`, `JpgImage`, `WebpImage`, `SvgImage`, `PDF`, `WordDocument`, `ExcelDocument`, `PowerpointDocument`.

  See [docs/typed-data.md](docs/typed-data.md) for the full guide.

---

## [0.1.7] — 2026-02-19

Initial published version.

- `create_granule` — sign data + metadata into a granule
- `verify` — verify granules, signed dicts, and signed files
- `content_hash` — BLAKE3 Merkle hash (returned plain hex string)
- `sign_and_embed_dict` — sign a dict with Unicode steganography
- `sign_and_embed` — embed signature in PNG/JPG/PDF/DOCX/XLSX/PPTX
- `extract_metadata` / `extract_signature` — read embedded data
- `strip_metadata_and_signature` — recover original file content
- `generate_key_pair` / `save_key` / `load_key` / `key_from_env` — key management
