# Writing Tests for MSD SDK

This SDK uses a declarative test pattern with Zef's `ET.UnitTest` entity. Each pure function gets its own test file in `tests/`.

## Test File Structure

Each test file follows this structure:
1. Test cases array (with UIDs and expected values)
2. Test execution code
3. Generation pipeline (commented out after initial use)

## Step-by-Step Guide

### Step 1: Write Initial Test Cases

Write test cases WITHOUT UIDs and WITHOUT expected values:

```python
#%%
from zef import *
import msd_sdk as msd

# Initial test data - no UIDs, no expected values
test_cases = [
  ET.UnitTest(
    description='Hash a simple string',
    args=['Hello, Meta Structured Data!'],
  ),
  ET.UnitTest(
    description='Hash an empty string',
    args=[''],
  ),
  # ... more test cases
]
```

### Step 2: Run the Generation Pipeline

The generation pipeline fills in UIDs and expected values by running the function:

```python
#%%
# Generation pipeline - run once to populate test_cases with UIDs and expected
def generate_test_cases_with_expected(fn):
    """Generate test cases with UIDs and expected values filled in."""
    updated_cases = []
    for test in test_cases:
        # Add UID if missing
        if not has_uid(test):
            test = test | set_uid(generate_uid) | collect
        
        # Calculate expected value
        args = test['args']
        expected = fn(*args)
        
        # Build new UnitTest with expected value
        test = ET.UnitTest(
            uid(test),
            description=test['description'],
            args=args,
            expected=expected
        )
        updated_cases.append(test)
    
    return updated_cases

# Run and copy to clipboard
generate_test_cases_with_expected(msd.content_hash) | repr_ | to_clipboard | run
```

**Important**: The user runs this code to generate the test cases. The output is copied directly to the clipboard via `to_clipboard | run`.

### Step 3: Update Test Cases

Replace the original `test_cases` array with the generated output (paste from clipboard). Comment out the generation code.

### Step 4: Add the Test Runner

```python
#%%
def run_tests(test_cases, fn):
    """Run all tests and report results."""
    failed_tests = []
    
    for test in test_cases:
        args = test['args']
        evaluated = fn(*args)
        expected = test['expected']
        
        if expected != evaluated:
            failed_tests.append({
                'description': test['description'],
                'args': args,
                'expected': expected,
                'evaluated': evaluated,
            })
    
    return failed_tests

failed_tests = run_tests(test_cases, msd.content_hash)

if len(failed_tests) == 0:
    print(f"✅ All {len(test_cases)} tests passed!")
else:
    print(f"❌ {len(failed_tests)} test(s) failed:")
    for test in failed_tests:
        print(f"  - {test['description']}")
        print(f"    Expected: {test['expected']}")
        print(f"    Got: {test['evaluated']}")
```

## Key Points

- **Use direct field access**: `test['expected']` not `test.get('expected')` (Zef entities don't have `.get()`)
- **MSD functions can't be used inside Zef operators** like `unpack()` - use Python loops instead
- **Each pure function gets its own test file**: `test_content_hash.py`, `test_verify.py`, etc.
- **User runs generation code**: The generation pipeline is run by the user to populate UIDs and expected values, then results are copied to clipboard with `| to_clipboard | run`

## Example Test Files

See the following for complete examples:
- [tests/test_content_hash.py](../tests/test_content_hash.py) - Tests for `msd.content_hash()`
- [tests/test_verify.py](../tests/test_verify.py) - Tests for `msd.verify()`
