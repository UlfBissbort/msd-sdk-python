"""Tests for trust network store.

Tests use MSD_TRUST_NETWORK env var pointed at a temp directory,
so they never touch the real ~/.config/msd/ trust network.
"""

import json
import os
import tempfile

from msd_sdk.trust_network import (
    add_to_trust_network,
    remove_from_trust_network,
    get_trust_network,
    clear_trust_network,
    is_trusted,
    _validate_entity,
    _normalize_entity,
    _entity_matches,
    _add_entity,
    _remove_entity,
    _has_entity,
    _get_trust_network_path,
)


# ─── Test Fixtures ────────────────────────────────────────────────────────────

ALICE = {'__type': 'ET.GoogleAccount', 'email': 'alice@gmail.com'}
BOB = {'__type': 'ET.GoogleAccount', 'email': 'bob@gmail.com'}
ACME = {'__type': 'ET.Organization', 'url': 'https://acme.com'}


class _TempTrustNetwork:
    """Context manager that redirects trust network to a temp dir."""
    def __enter__(self):
        self.tmpdir = tempfile.mkdtemp(prefix='msd-trust-test-')
        self.path = os.path.join(self.tmpdir, 'trust-network.json')
        self._old_env = os.environ.get('MSD_TRUST_NETWORK')
        os.environ['MSD_TRUST_NETWORK'] = self.path
        return self

    def __exit__(self, *args):
        # Restore env
        if self._old_env is None:
            os.environ.pop('MSD_TRUST_NETWORK', None)
        else:
            os.environ['MSD_TRUST_NETWORK'] = self._old_env
        # Clean up temp files
        if os.path.exists(self.path):
            os.remove(self.path)
        tmp = self.path + '.tmp'
        if os.path.exists(tmp):
            os.remove(tmp)
        os.rmdir(self.tmpdir)


# ─── Pure Function Tests ──────────────────────────────────────────────────────

def test_validate_entity_valid():
    """Valid entities pass validation without error."""
    _validate_entity(ALICE)
    _validate_entity(BOB)
    _validate_entity(ACME)
    _validate_entity({'__type': 'ET.GoogleAccount', 'email': 'a@b.c', 'extra': 'field'})


def test_validate_entity_not_dict():
    """Non-dict raises ValueError."""
    try:
        _validate_entity("not a dict")
        assert False, "Should have raised"
    except ValueError as e:
        assert "must be a dict" in str(e)


def test_validate_entity_missing_type():
    """Missing __type raises ValueError."""
    try:
        _validate_entity({'email': 'test@test.com'})
        assert False, "Should have raised"
    except ValueError as e:
        assert "__type" in str(e)


def test_validate_entity_unknown_type():
    """Unknown __type raises ValueError with supported types listed."""
    try:
        _validate_entity({'__type': 'ET.Unknown'})
        assert False, "Should have raised"
    except ValueError as e:
        assert "Unknown entity type" in str(e)
        assert "ET.GoogleAccount" in str(e)


def test_validate_entity_missing_identity_field():
    """Missing identity field raises ValueError."""
    try:
        _validate_entity({'__type': 'ET.GoogleAccount'})
        assert False, "Should have raised"
    except ValueError as e:
        assert "email" in str(e)


def test_validate_entity_empty_identity():
    """Empty string identity raises ValueError."""
    try:
        _validate_entity({'__type': 'ET.GoogleAccount', 'email': ''})
        assert False, "Should have raised"
    except ValueError as e:
        assert "non-empty" in str(e)


def test_validate_entity_whitespace_identity():
    """Whitespace-only identity raises ValueError."""
    try:
        _validate_entity({'__type': 'ET.GoogleAccount', 'email': '   '})
        assert False, "Should have raised"
    except ValueError as e:
        assert "non-empty" in str(e)


def test_validate_entity_non_string_identity():
    """Non-string identity raises ValueError."""
    try:
        _validate_entity({'__type': 'ET.GoogleAccount', 'email': 42})
        assert False, "Should have raised"
    except ValueError as e:
        assert "non-empty string" in str(e)


def test_validate_entity_none_type():
    """None __type raises ValueError."""
    try:
        _validate_entity({'__type': None})
        assert False, "Should have raised"
    except ValueError as e:
        assert "must be a string" in str(e)


def test_normalize_email_lowercase():
    """Email is lowercased and stripped."""
    result = _normalize_entity({'__type': 'ET.GoogleAccount', 'email': '  ALICE@Gmail.COM  '})
    assert result['email'] == 'alice@gmail.com'


def test_normalize_url_trailing_slash():
    """URL trailing slash is stripped."""
    result = _normalize_entity({'__type': 'ET.Organization', 'url': 'https://acme.com/'})
    assert result['url'] == 'https://acme.com'


def test_normalize_url_multiple_trailing_slashes():
    """Multiple trailing slashes are stripped."""
    result = _normalize_entity({'__type': 'ET.Organization', 'url': 'https://acme.com///'})
    assert result['url'] == 'https://acme.com'


def test_normalize_preserves_extra_fields():
    """Extra fields are preserved through normalization."""
    entity = {'__type': 'ET.GoogleAccount', 'email': 'a@b.com', 'display_name': 'Alice'}
    result = _normalize_entity(entity)
    assert result['display_name'] == 'Alice'
    assert result is not entity  # returns a copy


def test_entity_matches_same():
    """Same type and identity match."""
    assert _entity_matches(ALICE, ALICE)
    assert _entity_matches(ACME, ACME)


def test_entity_matches_different_type():
    """Different types don't match."""
    assert not _entity_matches(ALICE, ACME)


def test_entity_matches_different_identity():
    """Same type, different identity don't match."""
    assert not _entity_matches(ALICE, BOB)


def test_add_entity_new():
    """Adding a new entity returns a new list."""
    result = _add_entity([], ALICE)
    assert len(result) == 1
    assert result[0] == ALICE


def test_add_entity_duplicate():
    """Adding a duplicate returns the same list object."""
    entries = [ALICE]
    result = _add_entity(entries, ALICE)
    assert result is entries  # identity check — same object


def test_remove_entity_present():
    """Removing a present entity returns without it."""
    result = _remove_entity([ALICE, BOB], ALICE)
    assert len(result) == 1
    assert result[0] == BOB


def test_remove_entity_absent():
    """Removing an absent entity returns full list."""
    result = _remove_entity([ALICE], BOB)
    assert len(result) == 1


def test_has_entity():
    """has_entity correctly checks presence."""
    assert _has_entity([ALICE, BOB], ALICE)
    assert not _has_entity([ALICE], ACME)
    assert not _has_entity([], ALICE)


# ─── IO / Integration Tests ──────────────────────────────────────────────────

def test_empty_by_default():
    """Empty trust network when no file exists."""
    with _TempTrustNetwork():
        assert get_trust_network() == []


def test_add_creates_file():
    """Adding an entity creates the file."""
    with _TempTrustNetwork() as t:
        add_to_trust_network(ALICE)
        assert os.path.exists(t.path)
        assert len(get_trust_network()) == 1


def test_add_idempotent():
    """Adding same entity twice doesn't duplicate."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        add_to_trust_network(ALICE)
        assert len(get_trust_network()) == 1


def test_add_case_insensitive_email():
    """Email matching is case-insensitive."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        add_to_trust_network({'__type': 'ET.GoogleAccount', 'email': 'ALICE@GMAIL.COM'})
        assert len(get_trust_network()) == 1


def test_add_url_with_trailing_slash():
    """URL trailing slash doesn't create duplicate."""
    with _TempTrustNetwork():
        add_to_trust_network(ACME)
        add_to_trust_network({'__type': 'ET.Organization', 'url': 'https://acme.com/'})
        assert len(get_trust_network()) == 1


def test_add_multiple():
    """Adding different entities grows the list."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        add_to_trust_network(BOB)
        add_to_trust_network(ACME)
        assert len(get_trust_network()) == 3


def test_remove():
    """Removing an entity shrinks the list."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        add_to_trust_network(BOB)
        remove_from_trust_network(ALICE)
        network = get_trust_network()
        assert len(network) == 1
        assert network[0]['email'] == 'bob@gmail.com'


def test_remove_nonexistent():
    """Removing a non-existent entity is a no-op."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        remove_from_trust_network(BOB)
        assert len(get_trust_network()) == 1


def test_clear():
    """Clear removes all entries and deletes file."""
    with _TempTrustNetwork() as t:
        add_to_trust_network(ALICE)
        add_to_trust_network(ACME)
        clear_trust_network()
        assert get_trust_network() == []
        assert not os.path.exists(t.path)


def test_clear_when_empty():
    """Clear when no file exists is a no-op."""
    with _TempTrustNetwork():
        clear_trust_network()  # should not raise
        assert get_trust_network() == []


def test_is_trusted_present():
    """is_trusted returns True for trusted entities."""
    with _TempTrustNetwork():
        add_to_trust_network(ALICE)
        assert is_trusted(ALICE)
        assert is_trusted({'__type': 'ET.GoogleAccount', 'email': 'ALICE@Gmail.com'})


def test_is_trusted_absent():
    """is_trusted returns False for unknown entities."""
    with _TempTrustNetwork():
        assert not is_trusted(ALICE)


def test_stored_form_normalized():
    """On-disk form has normalized email/URL."""
    with _TempTrustNetwork() as t:
        add_to_trust_network({'__type': 'ET.GoogleAccount', 'email': '  BOB@Gmail.COM  '})
        with open(t.path) as f:
            data = json.load(f)
        assert data[0]['email'] == 'bob@gmail.com'


def test_extra_fields_preserved():
    """Extra fields on entities survive round-trip."""
    with _TempTrustNetwork():
        entity = {
            '__type': 'ET.GoogleAccount',
            'email': 'charlie@gmail.com',
            'display_name': 'Charlie',
        }
        add_to_trust_network(entity)
        stored = get_trust_network()
        assert stored[0]['display_name'] == 'Charlie'


def test_malformed_json_file():
    """Malformed JSON raises ValueError."""
    with _TempTrustNetwork() as t:
        with open(t.path, 'w') as f:
            f.write("not json{{{")
        try:
            get_trust_network()
            assert False, "Should have raised"
        except ValueError as e:
            assert "not valid JSON" in str(e)


def test_non_array_json():
    """Non-array JSON raises ValueError."""
    with _TempTrustNetwork() as t:
        with open(t.path, 'w') as f:
            json.dump({"not": "array"}, f)
        try:
            get_trust_network()
            assert False, "Should have raised"
        except ValueError as e:
            assert "JSON array" in str(e)


def test_env_var_override():
    """MSD_TRUST_NETWORK env var overrides default path."""
    with _TempTrustNetwork() as t:
        assert _get_trust_network_path() == t.path


def test_nested_directory_creation():
    """Deeply nested directories are created automatically."""
    with tempfile.TemporaryDirectory(prefix='msd-trust-test-') as tmpdir:
        deep_path = os.path.join(tmpdir, 'a', 'b', 'c', 'trust-network.json')
        old_env = os.environ.get('MSD_TRUST_NETWORK')
        os.environ['MSD_TRUST_NETWORK'] = deep_path
        try:
            add_to_trust_network(ALICE)
            assert os.path.exists(deep_path)
            assert len(get_trust_network()) == 1
        finally:
            if old_env is None:
                os.environ.pop('MSD_TRUST_NETWORK', None)
            else:
                os.environ['MSD_TRUST_NETWORK'] = old_env


def test_file_is_human_readable_json():
    """On-disk file is indented, human-readable JSON."""
    with _TempTrustNetwork() as t:
        add_to_trust_network(ALICE)
        with open(t.path) as f:
            raw = f.read()
        assert '\n' in raw  # indented, not single-line
        assert raw.endswith('\n')  # trailing newline
        parsed = json.loads(raw)
        assert isinstance(parsed, list)


def test_no_tmp_file_left_behind():
    """Atomic write doesn't leave .tmp file."""
    with _TempTrustNetwork() as t:
        add_to_trust_network(ALICE)
        assert not os.path.exists(t.path + '.tmp')


# ─── Runner ───────────────────────────────────────────────────────────────────

def _run_tests():
    """Run all tests and report results."""
    import inspect
    test_funcs = [
        (name, func) for name, func in sorted(globals().items())
        if name.startswith('test_') and callable(func)
    ]

    passed = 0
    failed = 0
    for name, func in test_funcs:
        try:
            func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ❌ {name}: {e}")

    total = passed + failed
    if failed == 0:
        print(f"\n✅ All {total} tests passed!")
    else:
        print(f"\n❌ {passed}/{total} passed, {failed} failed")
        exit(1)


if __name__ == '__main__':
    _run_tests()
