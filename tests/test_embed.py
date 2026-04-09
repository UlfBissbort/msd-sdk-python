#%%
"""
Test file for embed() function.

embed() takes an ET.SignedData dict (from sign()) and embeds the signature
into the data — either as binary embedding in files (PngImage, PDF, etc.)
or as Unicode steganography in plain dicts (__msd key).
"""

from zef import *
import msd_sdk as msd
import base64
import json


# Sample key from README.md for testing
sample_key = {
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}


def _create_minimal_png():
    """Create a minimal valid 1x1 pixel PNG for testing."""
    import struct
    import zlib
    
    signature = b'\x89PNG\r\n\x1a\n'
    
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc
    
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw_data = b'\x00\xff\x00\x00'
    compressed = zlib.compress(raw_data)
    
    return signature + chunk(b'IHDR', ihdr_data) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')


# ============================================================================
# Test 1: embed(sign(dict_data)) produces dict with __msd key
# ============================================================================

test_cases_dict_embed = [
  ('🍃-aa1bb2cc3dd4ee5ff6a7', 'embed dict produces __msd key',
   {'message': 'hello', 'count': 42}, {'creator': 'Alice'}),
  ('🍃-bb2cc3dd4ee5ff6a7b81', 'embed empty dict produces __msd key',
   {}, {'creator': 'Test'}),
  ('🍃-cc3dd4ee5ff6a7b81c92', 'embed nested dict produces __msd key',
   {'outer': {'inner': {'deep': True}}, 'list': [1, 2, 3]}, {'schema': 'v2'}),
]


def run_dict_embed_tests(test_cases):
    """Test that embed(sign(dict)) produces dict with __msd key."""
    failed = []
    
    for uid, desc, data, metadata in test_cases:
        signed = msd.sign(data, metadata, sample_key)
        
        try:
            embedded = msd.embed(signed)
        except Exception as e:
            failed.append({'description': desc, 'error': f'embed() raised: {e}'})
            continue
        
        # Must be a dict
        if not isinstance(embedded, dict):
            failed.append({'description': desc, 'error': f'Expected dict, got {type(embedded)}'})
            continue
        
        # Must have __msd key
        if '__msd' not in embedded:
            failed.append({'description': desc, 'error': 'Missing __msd key'})
            continue
        
        # __msd must start with 🔏
        if not embedded['__msd'].startswith('🔏'):
            failed.append({'description': desc, 'error': f'__msd does not start with 🔏'})
            continue
        
        # Original data keys must be preserved
        for k, v in data.items():
            if k not in embedded or embedded[k] != v:
                failed.append({'description': desc, 'error': f'Key {k} not preserved'})
                break
        else:
            # Must NOT have __type (it's a plain dict, not a signed entity)
            if '__type' in embedded:
                failed.append({'description': desc, 'error': f'Unexpected __type key in embedded dict'})
    
    return failed


# ============================================================================
# Test 2: embed(sign(png_data)) produces typed file dict
# ============================================================================

test_cases_file_embed = [
  ('🍃-dd4ee5ff6a7b81c92d03', 'embed PngImage produces typed dict'),
]


def run_file_embed_tests(test_cases):
    """Test that embed(sign(PngImage)) produces a typed file dict."""
    failed = []
    
    png_bytes = _create_minimal_png()
    png_b64 = base64.b64encode(png_bytes).decode()
    file_data = {'__type': 'PngImage', 'data': png_b64}
    metadata = {'creator': 'test', 'format': 'png'}
    
    signed = msd.sign(file_data, metadata, sample_key)
    
    try:
        embedded = msd.embed(signed)
    except Exception as e:
        failed.append({'description': 'embed PngImage produces typed dict', 'error': f'embed() raised: {e}'})
        return failed
    
    # Must be a typed PngImage dict
    if not isinstance(embedded, dict):
        failed.append({'description': 'embed PngImage produces typed dict', 'error': f'Expected dict, got {type(embedded)}'})
        return failed
    
    if embedded.get('__type') != 'PngImage':
        failed.append({'description': 'embed PngImage produces typed dict', 'error': f'Wrong __type: {embedded.get("__type")}'})
        return failed
    
    if 'data' not in embedded:
        failed.append({'description': 'embed PngImage produces typed dict', 'error': 'Missing data key'})
        return failed
    
    # Embedded data should be larger than original (has embedded signature)
    if len(embedded['data']) <= len(png_b64):
        failed.append({'description': 'embed PngImage produces typed dict', 'error': 'Embedded data not larger than original'})
        return failed
    
    return failed


# ============================================================================
# Test 3: embed output verifies with verify()
# ============================================================================

test_cases_verify = [
  ('🍃-ee5ff6a7b81c92d03e14', 'embedded dict verifies',
   {'message': 'hello'}, {'creator': 'Alice'}),
  ('🍃-ff6a7b81c92d03e14f25', 'embedded PngImage verifies'),
]


def run_verify_tests(test_cases):
    """Test that embed() output can be verified with verify()."""
    failed = []
    
    # Test dict embedding
    dict_data = {'message': 'hello'}
    dict_meta = {'creator': 'Alice'}
    signed_dict = msd.sign(dict_data, dict_meta, sample_key)
    embedded_dict = msd.embed(signed_dict)
    
    try:
        result = msd.verify(embedded_dict)
    except Exception as e:
        failed.append({'description': 'embedded dict verifies', 'error': f'verify raised: {e}'})
    else:
        if not result['signature_is_valid']:
            failed.append({'description': 'embedded dict verifies', 'error': 'Verification failed'})
    
    # Test file embedding
    png_bytes = _create_minimal_png()
    png_b64 = base64.b64encode(png_bytes).decode()
    file_data = {'__type': 'PngImage', 'data': png_b64}
    file_meta = {'creator': 'test'}
    signed_file = msd.sign(file_data, file_meta, sample_key)
    embedded_file = msd.embed(signed_file)
    
    try:
        result = msd.verify(embedded_file)
    except Exception as e:
        failed.append({'description': 'embedded PngImage verifies', 'error': f'verify raised: {e}'})
    else:
        if not result['signature_is_valid']:
            failed.append({'description': 'embedded PngImage verifies', 'error': 'Verification failed'})
    
    return failed


# ============================================================================
# Test 4: extract_metadata works on embed() output
# ============================================================================

test_cases_extract = [
  ('🍃-a71b82c93d04e15f2637', 'extract metadata from embedded dict'),
  ('🍃-b82c93d04e15f2637a48', 'extract metadata from embedded PngImage'),
]


def run_extract_tests(test_cases):
    """Test that metadata can be extracted from embed() output."""
    failed = []
    
    # Dict
    dict_data = {'payload': 'test'}
    dict_meta = {'creator': 'Alice', 'version': '1.0'}
    embedded_dict = msd.embed(msd.sign(dict_data, dict_meta, sample_key))
    
    try:
        extracted = msd.extract_metadata(embedded_dict)
        if extracted != dict_meta:
            failed.append({'description': 'extract metadata from embedded dict', 'error': f'Mismatch: {extracted} != {dict_meta}'})
    except Exception as e:
        failed.append({'description': 'extract metadata from embedded dict', 'error': f'Raised: {e}'})
    
    # File
    png_bytes = _create_minimal_png()
    file_data = {'__type': 'PngImage', 'data': base64.b64encode(png_bytes).decode()}
    file_meta = {'creator': 'test', 'format': 'png'}
    embedded_file = msd.embed(msd.sign(file_data, file_meta, sample_key))
    
    try:
        extracted = msd.extract_metadata(embedded_file)
        if extracted != file_meta:
            failed.append({'description': 'extract metadata from embedded PngImage', 'error': f'Mismatch: {extracted} != {file_meta}'})
    except Exception as e:
        failed.append({'description': 'extract metadata from embedded PngImage', 'error': f'Raised: {e}'})
    
    return failed


# ============================================================================
# Test 5: JSON round-trip for embedded dict
# ============================================================================

test_cases_json = [
  ('🍃-c93d04e15f2637a48b59', 'embedded dict survives JSON round-trip'),
]


def run_json_tests(test_cases):
    """Test that embed() dict output survives JSON serialization."""
    failed = []
    
    data = {'document': 'contract', 'value': 1000}
    meta = {'signer': 'legal'}
    embedded = msd.embed(msd.sign(data, meta, sample_key))
    
    json_str = json.dumps(embedded, ensure_ascii=False)
    restored = json.loads(json_str)
    
    try:
        result = msd.verify(restored)
    except Exception as e:
        failed.append({'description': 'embedded dict survives JSON round-trip', 'error': f'verify raised: {e}'})
        return failed
    
    if not result['signature_is_valid']:
        failed.append({'description': 'embedded dict survives JSON round-trip', 'error': 'Verification failed after JSON round-trip'})
    
    return failed


# ============================================================================
# Test 6: Error cases
# ============================================================================

test_cases_errors = [
  ('🍃-d04e15f2637a48b59c6a', 'embed rejects non-SignedData input'),
  ('🍃-e15f2637a48b59c6ad7b', 'embed rejects non-embeddable data (string)'),
  ('🍃-f2637a48b59c6ad7be8c', 'embed rejects dict with existing __msd'),
]


def run_error_tests(test_cases):
    """Test error handling for invalid inputs."""
    failed = []
    
    # Reject non-SignedData
    try:
        msd.embed({'__type': 'ET.SomethingElse', 'data': 'hello'})
        failed.append({'description': 'Rejects non-SignedData', 'error': 'Should have raised ValueError'})
    except ValueError:
        pass
    except Exception as e:
        failed.append({'description': 'Rejects non-SignedData', 'error': f'Wrong exception: {type(e).__name__}: {e}'})
    
    # Reject non-embeddable data (string in data field)
    signed_str = msd.sign('just a string', {}, sample_key)
    try:
        msd.embed(signed_str)
        failed.append({'description': 'Rejects non-embeddable data', 'error': 'Should have raised ValueError'})
    except ValueError:
        pass
    except Exception as e:
        failed.append({'description': 'Rejects non-embeddable data', 'error': f'Wrong exception: {type(e).__name__}: {e}'})
    
    # Reject dict with existing __msd
    signed_msd = msd.sign({'__msd': 'already here', 'other': 'data'}, {}, sample_key)
    try:
        msd.embed(signed_msd)
        failed.append({'description': 'Rejects dict with existing __msd', 'error': 'Should have raised ValueError'})
    except ValueError:
        pass
    except Exception as e:
        failed.append({'description': 'Rejects dict with existing __msd', 'error': f'Wrong exception: {type(e).__name__}: {e}'})
    
    return failed


# ============================================================================
# Test 7: Re-signing already-signed file (Risk 6 test)
# ============================================================================

test_cases_resign = [
  ('🍃-a37b48c59d6ae7bf8c9d', 'resigning already-signed PNG verifies'),
]


def run_resign_tests(test_cases):
    """Test that sign() correctly strips embedded data before re-signing."""
    failed = []
    
    png_bytes = _create_minimal_png()
    png_b64 = base64.b64encode(png_bytes).decode()
    file_data = {'__type': 'PngImage', 'data': png_b64}
    metadata = {'creator': 'test', 'version': '1'}
    
    # Sign and embed once
    first_signed = msd.sign(file_data, metadata, sample_key)
    first_embedded = msd.embed(first_signed)
    
    # Re-sign the already-embedded file with new metadata
    second_signed = msd.sign(first_embedded, {'creator': 'test', 'version': '2'}, sample_key)
    second_embedded = msd.embed(second_signed)
    
    # Must verify
    try:
        result = msd.verify(second_embedded)
    except Exception as e:
        failed.append({'description': 'resigning already-signed PNG verifies', 'error': f'verify raised: {e}'})
        return failed
    
    if not result['signature_is_valid']:
        failed.append({'description': 'resigning already-signed PNG verifies', 'error': 'Re-signed file failed verification (Risk 6)'})
    
    return failed


# ============================================================================
# Run all test groups
# ============================================================================

all_groups = [
    ("Dict embedding", run_dict_embed_tests, test_cases_dict_embed),
    ("File embedding", run_file_embed_tests, test_cases_file_embed),
    ("Verify round-trip", run_verify_tests, test_cases_verify),
    ("Extract metadata", run_extract_tests, test_cases_extract),
    ("JSON round-trip", run_json_tests, test_cases_json),
    ("Error handling", run_error_tests, test_cases_errors),
    ("Re-signing (Risk 6)", run_resign_tests, test_cases_resign),
]

total_passed = 0
total_failed = 0

for group_name, runner, cases in all_groups:
    failed = runner(cases)
    passed = len(cases) - len(failed)
    total_passed += passed
    total_failed += len(failed)
    
    if failed:
        print(f"❌ {group_name}: {len(failed)}/{len(cases)} failed")
        for f in failed:
            print(f"   - {f['description']}: {f['error']}")
    else:
        print(f"✅ {group_name}: {len(cases)}/{len(cases)} passed")

total = total_passed + total_failed
print(f"\n{'✅' if total_failed == 0 else '❌'} All {total} tests: {total_passed} passed, {total_failed} failed")
