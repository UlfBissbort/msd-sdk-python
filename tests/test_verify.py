#%%
from zef import *
import msd_sdk as msd


# Test cases for verify() - takes a granule dict and returns True/False
test_cases = [
  ET.UnitTest('🍃-d0b48b579907088f75eb',
    description='Verify valid granule with string data (complete metadata)',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Alice', 'description': 'sample data'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-7aa0801f3eaec65ffc4aa38c316ef3fcb56d987ff047cbbca3f80646b168ef2660b66d1373745'
            '305d43ab004f36b33db6b9e58d6436fa242bbd7f6752109c70c'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=True
  ),
  ET.UnitTest('🍃-86639ad287701cc4df6a',
    description='Verify tampered granule (data modified)',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'TAMPERED DATA',
        'metadata': {'creator': 'Alice'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-7aa0801f3eaec65ffc4aa38c316ef3fcb56d987ff047cbbca3f80646b168ef2660b66d1373745'
            '305d43ab004f36b33db6b9e58d6436fa242bbd7f6752109c70c'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=False
  ),
  ET.UnitTest('🍃-feba3f8a03f1e373273a',
    description='Verify tampered granule (metadata modified)',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Eve'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-7aa0801f3eaec65ffc4aa38c316ef3fcb56d987ff047cbbca3f80646b168ef2660b66d1373745'
            '305d43ab004f36b33db6b9e58d6436fa242bbd7f6752109c70c'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=False
  ),
  ET.UnitTest('🍃-f4f3bda5e8c1f6db6301',
    description='Verify valid granule with dict data',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': {'message': 'Hello', 'count': 42, 'nested': {'key': 'value'}},
        'metadata': {'creator': 'Bob', 'schema': 'v1.0'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-6bcfd1f137e103577fcdeefc35333bc15773ec080322807a7b82233eb5267d31e921949278682'
            'bbdb3e560948e892969bde19202e9feae36ca2dc9708b120f00'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=True
  ),
  ET.UnitTest('🍃-e30e177347d120fb5277',
    description='Verify tampered signature (invalid signature bytes)',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Alice', 'description': 'sample data'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-000000000000000000000000000000000000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000000000000'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=False
  ),
  ET.UnitTest('🍃-177bafc341f1ffef3a74',
    description='Verify wrong public key',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Alice', 'description': 'sample data'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1775630689'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-7aa0801f3eaec65ffc4aa38c316ef3fcb56d987ff047cbbca3f80646b168ef2660b66d1373745'
            '305d43ab004f36b33db6b9e58d6436fa242bbd7f6752109c70c'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-0000000000000000000000000000000000000000000000000000000000000000'
        }
      }
    ],
    expected=False
  ),
  ET.UnitTest('🍃-aefb998b6c9a6dfeb8d7',
    description='Verify tampered timestamp',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Alice', 'description': 'sample data'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '9999999999'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-7aa0801f3eaec65ffc4aa38c316ef3fcb56d987ff047cbbca3f80646b168ef2660b66d1373745'
            '305d43ab004f36b33db6b9e58d6436fa242bbd7f6752109c70c'
          )
        },
        'key': {
          '__type': 'ET.Ed25519KeyPair',
          '__uid': '🍃-8d1dc8766070c87a4bb1',
          'public_key': '🔑-8614d100b3cdb5ff6c37c846760dd1990f637994bd985d9486f212133bfd6284'
        }
      }
    ],
    expected=False
  )
]


#%%
# ============================================================================
# Test Execution - using Python loops since msd functions can't be used in ops
# ============================================================================

def run_tests(test_cases):
    """Run all tests and report results."""
    failed_tests = []
    
    for test in test_cases:
        args = test['args']
        evaluated = msd.verify(*args)
        expected = test['expected']
        
        if expected != evaluated:
            failed_tests.append({
                'description': test['description'],
                'args': args,
                'expected': expected,
                'evaluated': evaluated,
            })
    
    return failed_tests


failed_tests = run_tests(test_cases)

if len(failed_tests) == 0:
    print(f"✅ All {len(test_cases)} tests passed!")
else:
    print(f"❌ {len(failed_tests)} test(s) failed:")
    for test in failed_tests:
        print("\n================================")
        print(f"  - {test['description']}")
        print(f"    Expected: {test['expected']}")
        print(f"    Got: {test['evaluated']}")


#%%
# ============================================================================
# Generation pipeline - uncomment to generate UIDs and expected values
# ============================================================================

# def generate_test_cases_with_expected():
#     """Generate test cases with UIDs and expected values filled in."""
#     updated_cases = []
#     for test in test_cases:
#         # Add UID if missing
#         if not has_uid(test):
#             test = test | set_uid(generate_uid) | collect
        
#         # Calculate expected value
#         args = test['args']
#         expected = msd.verify(*args)
        
#         # Build new UnitTest with expected value
#         test = ET.UnitTest(
#             uid(test),
#             description=test['description'],
#             args=args,
#             expected=expected
#         )
#         updated_cases.append(test)
    
#     # Print for copy-paste back into test_cases
#     print(updated_cases | repr_ | collect)
#     return updated_cases

# # Uncomment to generate:
# generate_test_cases_with_expected() | repr_ | to_clipboard | run
