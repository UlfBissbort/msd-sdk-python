# MSD SDK Tutorial — Hands On

*Sign it. Verify it. Trust it.*

A hands-on walkthrough of the MSD SDK — using an **accounting audit trail** as the running example. Every code block is **self-contained**: run any block on its own.

> **Prerequisites:** `msd-sdk` and `zef` installed in the same virtual environment.


---

## 1. Your First Signed Invoice

A **Granule** is the fundamental unit of MSD: data + metadata + timestamp + cryptographic signature, bundled into a tamper-proof envelope.

```python
import msd_sdk as msd

# Test key pair — never use in production!
my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

invoice = {
    "invoice_id": "INV-2025-0042",
    "vendor": "Acme Supplies",
    "amount": 1250.00,
    "currency": "EUR",
    "line_items": [
        {"description": "Office chairs (x5)", "amount": 750.00},
        {"description": "Standing desks (x2)", "amount": 500.00},
    ]
}

audit = {
    "approved_by": "CFO Jane Chen",
    "department": "Operations",
    "approval_date": "2025-01-15",
}

granule = msd.create_granule(invoice, audit, my_key)
granule
```
````Result
{
  '__type': 'ET.SignedGranule',
  'data': {
    'invoice_id': 'INV-2025-0042',
    'vendor': 'Acme Supplies',
    'amount': 1250.0,
    'currency': 'EUR',
    'line_items': [
      {'description': 'Office chairs (x5)', 'amount': 750.0},
      {'description': 'Standing desks (x2)', 'amount': 500.0}
    ]
  },
  'metadata': {
    'approved_by': 'CFO Jane Chen',
    'department': 'Operations',
    'approval_date': '2025-01-15'
  },
  'signature_time': {'__type': 'Time', 'zef_unix_time': '1771462767'},
  'signature': {
    '__type': 'ET.Ed25519Signature',
    'signature': (
      '🔏-51d6a835632b70579145a9fee2fe3c190ccc11daef3c27ffbb9cec1a24364e64309ae2936a4'
      'ec10b093cbb1d7cca0c674ff8fa18b75d031dd256d771d8352208'
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

The granule contains `data` (the invoice), `metadata` (the audit trail), `signature_time`, `signature`, and `key` (public only — your private key never leaks).


---

## 2. Verify Before You Pay

Anyone with the public key can check: *has this invoice been tampered with since approval?*

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

granule = msd.create_granule(
    {"invoice_id": "INV-2025-0042", "amount": 1250.00, "vendor": "Acme Supplies"},
    {"approved_by": "CFO Jane Chen", "department": "Operations"},
    my_key
)

msd.verify(granule)
```
````Result
True
````
````Side Effects
[]
````


---

## 3. Content-Addressable Invoices

Need a unique fingerprint for deduplication or lookups — without signing? `content_hash` gives you a deterministic BLAKE3 Merkle hash.

```python
import msd_sdk as msd

inv_a = msd.content_hash({"invoice_id": "INV-2025-0042", "amount": 1250.00})
inv_b = msd.content_hash({"invoice_id": "INV-2025-0042", "amount": 1250.00})
inv_c = msd.content_hash({"invoice_id": "INV-2025-0043", "amount": 89.99})

("same invoice, same hash:", inv_a == inv_b, "different invoice, different hash:", inv_a != inv_c)
```
````Result
('same invoice, same hash:', True, 'different invoice, different hash:', True)
````
````Side Effects
[]
````


---

## 4. The Invisible Audit Trail — Unicode Steganography 🔏

Granules wrap your data in a new structure. But what if you want to keep the original dict shape — say, for an API response or a JSON export — while still carrying a cryptographic audit trail?

`sign_and_embed_dict` hides the full signature inside a single `🔏` emoji using **Unicode steganography**. Invisible variation selectors carry the complete metadata, timestamp, and Ed25519 signature. The dict stays clean and uncluttered.

```python
import msd_sdk as msd
import json

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

payment = {
    "invoice_id": "INV-2025-0042",
    "amount": 1250.00,
    "currency": "EUR",
    "vendor": "Acme Supplies",
    "paid_on": "2025-01-20",
}

audit_trail = {
    "approved_by": "CFO Jane Chen",
    "reviewed_by": "Controller Bob Park",
    "compliance_check": "passed",
}

signed = msd.sign_and_embed_dict(payment, audit_trail, my_key)

# The original data is untouched — plus a steganographic __msd key
# Survives JSON round-trips
json.loads(json.dumps(signed)) == signed
```
````Result
True
````
````Side Effects
[]
````


---

## 5. Reading the Audit Trail

Extract the metadata and signature hidden inside a signed dict:

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

signed = msd.sign_and_embed_dict(
    {"invoice_id": "INV-2025-0042", "amount": 1250.00},
    {"approved_by": "CFO Jane Chen", "compliance_check": "passed"},
    my_key
)

meta = msd.extract_metadata(signed)
sig = msd.extract_signature(signed)

{
    "audit_trail": meta,
    "signed_at": sig["signature_time"],
    "signing_key": sig["key"]["__uid"],
}
```
````Result
{'audit_trail': {'approved_by': 'CFO Jane Chen', 'compliance_check': 'passed'}, 'signed_at': {'__type': 'Time', 'zef_unix_time': '1771462875'}, 'signing_key': '🍃-8d1dc8766070c87a4bb1'}
````
````Side Effects
[]
````


---

## 6. Catching Fraud

Change anything in a signed dict — a value, add a key, remove a key — and `verify()` catches it.

```python
import msd_sdk as msd

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

expense = {"vendor": "Acme Supplies", "amount": 1250.00, "category": "office"}
signed = msd.sign_and_embed_dict(expense, {"approved_by": "CFO Jane Chen"}, my_key)

# Untouched: valid
original_ok = msd.verify(signed)

# Inflated amount
t1 = dict(signed); t1["amount"] = 9999.00
inflated_ok = msd.verify(t1)

# Snuck in a bonus line
t2 = dict(signed); t2["bonus"] = 500.00
added_ok = msd.verify(t2)

# Removed the category to hide it
t3 = {k: v for k, v in signed.items() if k != "category"}
removed_ok = msd.verify(t3)

{"original": original_ok, "inflated_amount": inflated_ok, "added_key": added_ok, "removed_key": removed_ok}
```
````Result
{'original': True, 'inflated_amount': False, 'added_key': False, 'removed_key': False}
````
````Side Effects
[]
````


---

## 7. Signing the Receipts

MSD can embed signatures directly into binary files — the signed file stays viewable by standard programs.

Supported formats: **PNG, JPG, PDF, DOCX, XLSX, PPTX**.

```python
import msd_sdk as msd
import struct, zlib

my_key = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}

# Minimal 1x1 red PNG (stand-in for a scanned receipt)
def make_tiny_png():
    sig = b'\x89PNG\r\n\x1a\n'
    def chunk(ct, d):
        c = ct + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    return sig + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00')) + chunk(b'IEND', b'')

receipt_png = make_tiny_png()

signed_receipt = msd.sign_and_embed(
    {'type': 'png', 'content': receipt_png},
    {'expense_report': 'EXP-2025-007', 'scanned_by': 'Accounting Dept'},
    my_key
)

meta = msd.extract_metadata(signed_receipt)
valid = msd.verify(signed_receipt)
clean = msd.strip_metadata_and_signature(signed_receipt)

{
    "embedded_audit": meta,
    "signature_valid": valid,
    "original_recovered": clean['content'] == receipt_png,
}
```
````Result
{'embedded_audit': {'expense_report': 'EXP-2025-007', 'scanned_by': 'Accounting Dept'}, 'signature_valid': True, 'original_recovered': True}
````
````Side Effects
[]
````


---

## Quick Reference

| What you want to do | Function |
|---|---|
| Sign data into a granule | `msd.create_granule(data, metadata, key)` |
| Sign a dict (Unicode steganography) | `msd.sign_and_embed_dict(data, metadata, key)` |
| Sign a file (PNG, PDF, etc.) | `msd.sign_and_embed({'type': ..., 'content': ...}, metadata, key)` |
| Verify any signed data | `msd.verify(signed_data)` |
| Extract metadata | `msd.extract_metadata(signed_data)` |
| Extract signature info | `msd.extract_signature(signed_data)` |
| Content hash (no signing) | `msd.content_hash(data)` |
| Strip signature from file | `msd.strip_metadata_and_signature(signed_file)` |
| Load key from env var | `msd.key_from_env("MSD_PRIVATE_KEY")` |
