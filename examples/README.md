# MSD-SDK Examples

This folder contains examples demonstrating how to use the MSD-SDK for signing and embedding metadata into various file formats.

## Supported File Formats

| Format | Type Key | Description |
|--------|----------|-------------|
| PNG | `png` | PNG images |
| JPG | `jpg` | JPEG images |
| PDF | `pdf` | PDF documents |
| DOCX | `word_document` | Microsoft Word documents |
| XLSX | `excel_document` | Microsoft Excel spreadsheets |
| PPTX | `powerpoint_document` | Microsoft PowerPoint presentations |

## Running the Example

```bash
# From the repository root:
python examples/sign_and_embed_example.py
```

## Example Output

```
FILE: sample2.png
TYPE: png

1. Original file: 48,941 bytes
   SHA256: 7462633dfd25ef299b1b0219...

2. Signed file: 49,127 bytes
   Metadata embedded: {'author': 'test_user', 'version': '1.0'}

3. Saved signed file to: examples/signed_output/signed_sample2.png

4. Extracted metadata: {'author': 'test_user', 'version': '1.0'}
   Matches original: ✓

5. Stripped file: 48,746 bytes
   Matches canonical: ✓
   Note: Original had 195 bytes of extra metadata
```

## Sample Files

The `sample_files/` directory contains test files for each supported format:

- `sample2.png` - Sample PNG image
- `sample2.jpg` - Sample JPEG image
- `sample.pdf` - Sample PDF document
- `sample.docx` - Sample Word document
- `sample.xlsx` - Sample Excel spreadsheet
- `sample.pptx` - Sample PowerPoint presentation

## Key Concepts

### Canonical Form

When signing, MSD-SDK first strips any existing embedded data to create a "canonical" version of the file. This ensures:

1. **Idempotency**: Signing the same file twice produces consistent results
2. **Roundtrip integrity**: `strip(sign(canonical)) == canonical`

For most formats (JPG, DOCX, XLSX, PPTX), the canonical form equals the original. For PNG, some extra metadata chunks may be normalized.

### Metadata Structure

Metadata can be any JSON-serializable dictionary:

```python
metadata = {
    'author': 'John Doe',
    'created': '2024-01-15',
    'confidential': True,
    'version': 1
}
```

### Signing Key

The examples use a test key. In production, use:

```python
import msd_sdk as msd

# Load key from environment variable
key = msd.key_from_env('MSD_SIGNING_KEY')
```
