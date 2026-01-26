#!/usr/bin/env python3
"""
Example: Sign and embed metadata into various file formats.

This example demonstrates:
1. Loading a file
2. Signing and embedding metadata
3. Saving the signed file
4. Loading and extracting metadata
5. Stripping metadata to recover original content

Supported formats: PNG, JPG, PDF, DOCX, XLSX, PPTX
"""

import os
import hashlib
import msd_sdk as msd

# Example key - in production, use msd.key_from_env() or generate securely
EXAMPLE_KEY = {
    '__type': 'ET.Ed25519KeyPair',
    '__uid': '🍃-8d1dc8766070c87a4bb1',
    'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
    'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}


def sha256_hash(data: bytes) -> str:
    """Compute SHA256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def demo_sign_and_extract(file_path: str, file_type: str, metadata: dict):
    """Demonstrate signing, extracting, and stripping for a file."""
    
    print(f"\n{'=' * 60}")
    print(f"FILE: {os.path.basename(file_path)}")
    print(f"TYPE: {file_type}")
    print(f"{'=' * 60}")
    
    # 1. Load original file
    with open(file_path, 'rb') as f:
        original_content = f.read()
    
    original_hash = sha256_hash(original_content)
    print(f"\n1. Original file: {len(original_content):,} bytes")
    print(f"   SHA256: {original_hash[:32]}...")
    
    # 2. Sign and embed metadata
    data = {'type': file_type, 'content': original_content}
    signed = msd.sign_and_embed(data, metadata, EXAMPLE_KEY)
    
    print(f"\n2. Signed file: {len(signed['content']):,} bytes")
    print(f"   Metadata embedded: {metadata}")
    
    # 3. Save signed file
    output_dir = os.path.join(os.path.dirname(file_path), '..', 'signed_output')
    os.makedirs(output_dir, exist_ok=True)
    signed_path = os.path.join(output_dir, f"signed_{os.path.basename(file_path)}")
    
    with open(signed_path, 'wb') as f:
        f.write(signed['content'])
    print(f"\n3. Saved signed file to: {signed_path}")
    
    # 4. Load and extract metadata
    with open(signed_path, 'rb') as f:
        loaded_content = f.read()
    
    loaded_data = {'type': file_type, 'content': loaded_content}
    extracted = msd.extract_metadata(loaded_data)
    
    print(f"\n4. Extracted metadata: {extracted}")
    print(f"   Matches original: {'✓' if extracted == metadata else '✗'}")
    
    # 5. Strip metadata to recover original
    stripped = msd.strip_metadata_and_signature(loaded_data)
    stripped_hash = sha256_hash(stripped['content'])
    
    # Note: For PNG, original may have extra metadata that gets normalized
    # For other formats, stripped should match original exactly
    canonical_data = {'type': file_type, 'content': original_content}
    canonical = msd.strip_metadata_and_signature(canonical_data)
    canonical_hash = sha256_hash(canonical['content'])
    
    print(f"\n5. Stripped file: {len(stripped['content']):,} bytes")
    print(f"   Matches canonical: {'✓' if stripped_hash == canonical_hash else '✗'}")
    
    if original_content != canonical['content']:
        diff = len(original_content) - len(canonical['content'])
        print(f"   Note: Original had {diff} bytes of extra metadata")
    
    return extracted == metadata and stripped_hash == canonical_hash


def main():
    """Run examples for all supported file formats."""
    
    print("\n" + "=" * 60)
    print("MSD-SDK EMBEDDING EXAMPLES")
    print("=" * 60)
    
    base_dir = os.path.dirname(__file__)
    sample_dir = os.path.join(base_dir, 'sample_files')
    
    examples = [
        ('sample2.png', 'png', {'author': 'test_user', 'version': '1.0'}),
        ('sample2.jpg', 'jpg', {'author': 'photographer', 'camera': 'digital'}),
        ('sample.pdf', 'pdf', {'author': 'document_creator', 'department': 'engineering'}),
        ('sample.docx', 'word_document', {'author': 'writer', 'confidential': True}),
        ('sample.xlsx', 'excel_document', {'author': 'analyst', 'quarter': 4}),
        ('sample.pptx', 'powerpoint_document', {'author': 'presenter', 'slides': 1}),
    ]
    
    results = []
    
    for filename, file_type, metadata in examples:
        file_path = os.path.join(sample_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"\nSkipping {filename}: file not found")
            continue
        
        try:
            success = demo_sign_and_extract(file_path, file_type, metadata)
            results.append((filename, 'PASS' if success else 'FAIL'))
        except Exception as e:
            print(f"\nError processing {filename}: {e}")
            results.append((filename, 'ERROR'))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for filename, status in results:
        emoji = '✓' if status == 'PASS' else '✗'
        print(f"  {emoji} {filename}: {status}")
    
    passed = sum(1 for _, s in results if s == 'PASS')
    print(f"\n{passed}/{len(results)} examples completed successfully")


if __name__ == '__main__':
    main()
