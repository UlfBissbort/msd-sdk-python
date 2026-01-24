#%%
from zef import *
import msd_sdk as msd


# Test data for content_hash - following declarative test pattern
# UIDs and expected values will be filled in automatically
test_cases = [
  ET.UnitTest('🍃-954c268be37c6d28bea1',
    description='Hash a simple string',
    args=['Hello, Meta Structured Data!'],
    expected=String(hash='🪨-523d1d9f304a40f30aa741cbdd66cad80f65b9db6c6cba66f2e149e0c2907f29')
  ),
  ET.UnitTest('🍃-7fc83d7e65977233182c',
    description='Hash an empty string',
    args=[''],
    expected=String(hash='🪨-928d2f9f582b4423e27990762d3ce78ab9106a1aa7001f998b0378a941850f38')
  ),
  ET.UnitTest('🍃-af54b232d86e1cb30d54',
    description='Hash an integer',
    args=[42],
    expected=Int('🪨-b80d336df28a0d02f8301151f8a3b04fd44e0752cccf15ec92547bd814a7e627')
  ),
  ET.UnitTest('🍃-170f056baf8e7881528f',
    description='Hash a float',
    args=[3.14159],
    expected=Float('🪨-cab1a4466c089183744562c8ffc9311c982bfb1d50cb0a67d1478f4ab70d8a5a')
  ),
  ET.UnitTest('🍃-2eb390db04bf52c61b6c',
    description='Hash a boolean True',
    args=[True],
    expected=Bool('🪨-16162b78c20357b8ff6ad078592da2ed4194efa3f38a3f9e223d8602f1a53720')
  ),
  ET.UnitTest('🍃-bcf454714385dd0b8652',
    description='Hash a boolean False',
    args=[False],
    expected=Bool('🪨-768c1694acfd4d0c29e174ac43d7e91ff36d412439c3c872eaba6a8d80accf33')
  ),
  ET.UnitTest('🍃-014c8cba4838e979ce0c',
    description='Hash None',
    args=[nil],
    expected=Nil('🪨-97ef5c3b3452890d7657a3743094f7a11a2074d9887d166f3e740b56e07c23e9')
  ),
  ET.UnitTest('🍃-ebff94bff303ba9422dc',
    description='Hash a simple dict',
    args=[{'key': 'value'}],
    expected=Dict('🪨-d81744a48dcd383d2286b53492359bafeeb678a003c1f1b5ff6f3bb0f9bcdf04')
  ),
  ET.UnitTest('🍃-9999a5c6f6dc70c4293a',
    description='Hash a nested dict',
    args=[{'outer': {'inner': 'value', 'count': 42}}],
    expected=Dict('🪨-99fb2eb38d925ac54e60125c76e2eb5f83460710082633576fb7bc5127d3d3a9')
  ),
  ET.UnitTest('🍃-d3d31f59d4cdc416268a',
    description='Hash a simple list',
    args=[[1, 2, 3]],
    expected=Array(hash='🪨-2718b44334acb3beb6dc14a75973cde66a61e248ba72b216c5d773a8b38150e7')
  ),
  ET.UnitTest('🍃-5c74a3aaac1981703687',
    description='Hash a mixed list',
    args=[[1, 'two', 3.0, True, nil]],
    expected=Array(hash='🪨-ddad5924a0a2b8407534ed93305beb5503d6a29ec49f42539c691de8907f6eef')
  ),
  ET.UnitTest('🍃-c8b9c6d6f29e9a388e31',
    description='Hash an empty dict',
    args=[{}],
    expected=Dict('🪨-ab13bedf42e84bae0f7c62c7dd6a8ada571e8829bed6ea558217f0361b5e25d0')
  ),
  ET.UnitTest('🍃-1226b2afaccfd5e58223',
    description='Hash an empty list',
    args=[[]],
    expected=Array(hash='🪨-af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262')
  )
]

# ============================================================================
# Test Execution - using Python loops since msd functions can't be used in ops
# ============================================================================

def run_tests(test_cases):
    """Run all tests and report results."""
    failed_tests = []
    
    for test in test_cases:
        # Get the args and unpack them to call msd.content_hash
        args = test['args']
        evaluated = msd.content_hash(*args)
        
        # Compare with expected - use direct access, not .get()
        expected = test['expected']
        matches = (expected == evaluated)
        if not matches:
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
        print(f"    Args: {test['args']}")
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
#         # Create a copy with UID if missing
#         if not has_uid(test):
#             test = test | set_uid(generate_uid) | collect
        
#         # Calculate expected value if missing
#         if 'expected' not in test:
#             args = test['args']
#             expected = msd.content_hash(*args)
#             print(test)
#             print(expected)
#             test = test | insert({'expected': expected}) | collect
        
#         updated_cases.append(test)
    
#     # Print as repr for copy-paste
#     result = updated_cases | repr_ | collect
#     print(result)
#     return updated_cases

# generate_test_cases_with_expected() | repr_ | to_clipboard | run


