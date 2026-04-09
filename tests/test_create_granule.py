#%%
"""
Test file for sign() function — structure and verification tests.

sign() is NON-DETERMINISTIC because it uses zef.now() internally.
Each call produces a different signature_time and therefore a different signature.

Current approach: Test structure, check data/metadata match, verify signature.
"""

from zef import *
import msd_sdk as msd


# Sample key from README.md for testing
sample_key = {
  '__type': 'ET.Ed25519KeyPair',
  '__uid': '🍃-8d1dc8766070c87a4bb1',
  'private_key': '🗝️-61250af6bf8b9332be5c2b8a4877c56189867c8840cce541ab7fbe9270bb9b6c',
  'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
}


# Test cases for sign(data, metadata, key)
test_cases = [
  ET.UnitTest(
    description='Sign string data',
    args=['Hello, Meta Structured Data!', {'creator': 'Alice', 'description': 'sample data'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign empty string',
    args=['', {'creator': 'Test'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign integer data',
    args=[42, {'type': 'number'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign float data',
    args=[3.14159, {'type': 'pi'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign boolean True',
    args=[True, {'type': 'boolean'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign boolean False',
    args=[False, {'type': 'boolean'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign None/nil',
    args=[nil, {'type': 'null'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign simple dict data',
    args=[{'message': 'Hello'}, {'creator': 'Bob'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign nested dict data',
    args=[{'outer': {'inner': 'value', 'count': 42}}, {'schema': 'v1'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign list data',
    args=[[1, 2, 3], {'type': 'array'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign mixed list',
    args=[[1, 'two', 3.0, True, nil], {'type': 'mixed'}, sample_key],
  ),
  ET.UnitTest(
    description='Sign with empty metadata',
    args=['data', {}, sample_key],
  ),
]


#%%
def run_tests(test_cases):
    """Run all tests and report results."""
    failed_tests = []
    
    for test in test_cases:
        args = test['args']
        data, metadata, key = args
        
        signed = msd.sign(data, metadata, key)
        
        # Check structure
        required_keys = {'__type', 'data', 'metadata', 'signature_time', 'signature', 'key'}
        actual_keys = set(signed.keys())
        if not required_keys.issubset(actual_keys):
            failed_tests.append({
                'description': test['description'],
                'error': f'Missing keys: {required_keys - actual_keys}',
            })
            continue
        
        # Check __type is ET.SignedData
        if signed['__type'] != 'ET.SignedData':
            failed_tests.append({
                'description': test['description'],
                'error': f'Wrong __type: {signed["__type"]}',
            })
            continue
        
        # Check data matches input
        expected_data = None if data == nil else data
        if signed['data'] != expected_data:
            failed_tests.append({
                'description': test['description'],
                'error': f'Data mismatch: expected {data}, got {signed["data"]}',
            })
            continue
        
        # Check metadata matches input
        if signed['metadata'] != metadata:
            failed_tests.append({
                'description': test['description'],
                'error': f'Metadata mismatch: expected {metadata}, got {signed["metadata"]}',
            })
            continue
        
        # Check it verifies correctly
        result = msd.verify(signed)
        if not result['signature_is_valid']:
            failed_tests.append({
                'description': test['description'],
                'error': 'Signature verification failed',
            })
    
    return failed_tests

#%%
failed = run_tests(test_cases)
total = len(test_cases)
passed = total - len(failed)

if failed:
    print(f"❌ {len(failed)}/{total} tests failed:")
    for f in failed:
        print(f"  - {f['description']}: {f['error']}")
else:
    print(f"✅ All {total} tests passed!")

print(f"\n{'✅' if not failed else '❌'} All {total} tests: {passed} passed, {len(failed)} failed")
