# Changelog

All notable changes to the MSD SDK are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
