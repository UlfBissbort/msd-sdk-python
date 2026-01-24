#%%
from zef import *
import msd_sdk as msd


# Initial test data - no UIDs, no expected values
# verify() takes a granule dict and returns True/False
test_cases = [
  ET.UnitTest('🍃-d0b48b579907088f75eb',
    description='Verify valid granule with string data',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'Hello, Meta Structured Data!',
        'metadata': {'creator': 'Alice'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-9f3a8c29e9784fe63ccc7ebc3e1f394e9dcdf9a7d51bc6fa314dac8a902e9aff6a4e64619ba'
            'e5a4f674980fcba77877d8a0131e8dfa7976cc23cf1d526ab0c07'
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
  ET.UnitTest('🍃-86639ad287701cc4df6a',
    description='Verify tampered granule (data modified)',
    args=[
      {
        '__type': 'ET.SignedGranule',
        'data': 'TAMPERED DATA',
        'metadata': {'creator': 'Alice'},
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-9f3a8c29e9784fe63ccc7ebc3e1f394e9dcdf9a7d51bc6fa314dac8a902e9aff6a4e64619ba'
            'e5a4f674980fcba77877d8a0131e8dfa7976cc23cf1d526ab0c07'
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
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-9f3a8c29e9784fe63ccc7ebc3e1f394e9dcdf9a7d51bc6fa314dac8a902e9aff6a4e64619ba'
            'e5a4f674980fcba77877d8a0131e8dfa7976cc23cf1d526ab0c07'
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
        'signature_time': {'__type': 'Time', 'zef_unix_time': '1769253762'},
        'signature': {
          '__type': 'ET.Ed25519Signature',
          'signature': (
            '🔏-04ae2907139456ea20a5d0812dfb14ff90abe010113142cbdfd1b8703aea0fc5bd279124904'
            '9789983d39f8c63851fb4175fec52993f7ea500931fd7eac32506'
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
